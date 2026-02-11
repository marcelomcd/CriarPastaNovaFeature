"""Orquestração: por Feature, criar pasta no SharePoint, link e sincronizar anexos."""
import logging
from collections import Counter
from datetime import datetime
from pathlib import Path

from app.models.devops_models import WorkItemResponse
from app.models.feature_folder import FeatureInfo, FeatureFolderPath
from app.services.devops_client import AzureDevOpsClient
from app.services.sharepoint_files import SharePointFileService
from app.utils.name_utils import (
    normalize_client_name,
    build_feature_folder_name,
)
from app.utils.pipeline_logger import log_feature_result

logger = logging.getLogger(__name__)


def _parse_created_date(fields: dict) -> datetime:
    """Extrai System.CreatedDate do work item (pode ser string ISO)."""
    raw = fields.get("System.CreatedDate")
    if raw is None:
        return datetime.now()
    if isinstance(raw, datetime):
        return raw
    try:
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except ValueError:
        return datetime.now()


def work_item_to_feature_info(wi: WorkItemResponse) -> FeatureInfo:
    """Converte WorkItemResponse em FeatureInfo."""
    fields = wi.fields
    created = _parse_created_date(fields)
    area = (fields.get("System.AreaPath") or "").strip()
    client_segment = area.split("\\")[-1] if area else ""
    return FeatureInfo(
        id=wi.id,
        title=(fields.get("System.Title") or "").strip(),
        area_path=area,
        created_date=created,
        state=(fields.get("System.State") or "").strip(),
        numero_proposta=fields.get("Custom.NumeroProposta"),
        link_pasta_documentacao=fields.get("Custom.LinkPastaDocumentacao"),
    )


# Estados considerados "encerrados" para colocar a pasta em Year/Closed/Cliente/Feature
CLOSED_STATES = frozenset({"encerrado", "closed", "concluído", "concluido", "resolved", "done", "resolvido"})


def _is_closed_state(state: str) -> bool:
    """Indica se o estado da Feature é considerado encerrado (pasta em Closed)."""
    return (state or "").strip().lower() in CLOSED_STATES


def feature_info_to_folder_path(info: FeatureInfo) -> FeatureFolderPath:
    """Converte FeatureInfo em FeatureFolderPath (nome da pasta e cliente normalizados). Features encerradas vão para Ano/Closed/Cliente/Feature."""
    client_name = normalize_client_name(info.area_path.split("\\")[-1] if info.area_path else "")
    folder_name = build_feature_folder_name(
        info.id,
        info.numero_proposta,
        info.title,
    )
    closed = _is_closed_state(info.state)
    return FeatureFolderPath(year=info.year, client_name=client_name, folder_name=folder_name, closed=closed)


class FeatureFolderService:
    """Orquestra criação de pasta no SharePoint, link e sincronização de anexos por Feature."""

    def __init__(
        self,
        devops_client: AzureDevOpsClient | None = None,
        sharepoint_service: SharePointFileService | None = None,
    ) -> None:
        self.devops = devops_client or AzureDevOpsClient()
        self.sharepoint = sharepoint_service or SharePointFileService()

    def process_feature(self, work_item_id: int, *, skip_work_item_update: bool = False) -> dict:
        """
        Para uma Feature: garante pasta no SharePoint, link e anexos (modo atualização).
        - Pasta: criada somente se ainda não existir.
        - Anexos: enviados somente os que ainda não estão na pasta (sem duplicar).
        - Link: atualizado no Azure DevOps apenas se estiver diferente (omitido se skip_work_item_update=True).
        skip_work_item_update: quando True, não atualiza Custom.LinkPastaDocumentacao (útil para itens que falham com 400 por campos obrigatórios).
        Retorna dict com folder_id, web_url, attachments_synced, etc.
        """
        wi = self.devops.get_work_item_by_id(work_item_id)
        if not wi:
            raise ValueError(f"Work item {work_item_id} não encontrado")
        if (wi.fields.get("System.WorkItemType") or "").strip() != "Feature":
            raise ValueError(f"Work item {work_item_id} não é uma Feature")

        info = work_item_to_feature_info(wi)
        path = feature_info_to_folder_path(info)
        relative = path.relative_path()

        drive_id, folder_id = self.sharepoint.ensure_folder_path(relative)

        # Se Feature encerrada e já existir pasta na localização ativa, mover conteúdo para Closed
        if path.closed:
            active_relative = path.relative_path_active()
            active_folder_id = self.sharepoint.get_folder_id_by_relative_path(drive_id, active_relative)
            if active_folder_id and active_folder_id != folder_id:
                try:
                    self.sharepoint.copy_folder_contents_to(drive_id, active_folder_id, folder_id)
                    logger.info("Feature %s: pasta movida de ativo para Closed", work_item_id)
                except Exception as e:
                    logger.warning("Feature %s: não foi possível mover pasta ativa para Closed: %s", work_item_id, e)

        web_url = self.sharepoint.create_sharing_link(drive_id, folder_id)

        if not skip_work_item_update:
            current_link = (wi.fields.get("Custom.LinkPastaDocumentacao") or "").strip()
            if current_link != web_url:
                updated = self.devops.update_work_item_link_pasta(work_item_id, web_url)
                if updated is not None:
                    logger.info("Atualizado Custom.LinkPastaDocumentacao para Feature %s", work_item_id)
                else:
                    logger.info("Feature %s: pasta e anexos ok; link não gravado no work item (validação Azure DevOps)", work_item_id)
        else:
            logger.info("Feature %s: pasta e anexos garantidos (atualização do work item omitida)", work_item_id)

        # Listar nomes já existentes na pasta para não duplicar anexos
        existing_names: set[str] = set()
        try:
            for item in self.sharepoint.list_folder_children(drive_id, folder_id):
                if item.get("file") is not None and item.get("name"):
                    existing_names.add((item.get("name") or "").strip())
        except Exception as e:
            logger.debug("Não foi possível listar arquivos existentes na pasta: %s", e)

        attachments_synced = 0
        attachment_names_uploaded: list[str] = []
        name_count: Counter[str] = Counter()
        for att_id, name in self.devops.list_attachment_relations(wi):
            try:
                tmp = self.devops.download_attachment(att_id, file_name=name)
                try:
                    base_name = tmp.name
                    if name_count[base_name] > 0:
                        stem, suffix = Path(base_name).stem, Path(base_name).suffix or ""
                        upload_name = f"{stem} ({name_count[base_name] + 1}){suffix}"
                    else:
                        upload_name = base_name
                    name_count[base_name] += 1
                    # Não duplicar: pular se já existir arquivo com o mesmo nome
                    if upload_name in existing_names:
                        logger.debug("Anexo já existe na pasta, ignorando: %s", upload_name)
                        continue
                    self.sharepoint.upload_file(
                        tmp, folder_id=folder_id, drive_id=drive_id, overwrite=True, upload_name=upload_name
                    )
                    attachments_synced += 1
                    attachment_names_uploaded.append(upload_name)
                    existing_names.add(upload_name)
                finally:
                    try:
                        tmp.unlink(missing_ok=True)
                    except OSError:
                        pass
            except Exception as e:
                logger.warning("Falha ao sincronizar anexo %s da Feature %s: %s", att_id, work_item_id, e)

        client_name = path.client_name
        titulo = info.title
        numero_proposta = (info.numero_proposta or "").strip() if info.numero_proposta else None
        log_feature_result(
            work_item_id=work_item_id,
            cliente=client_name,
            numero_proposta=numero_proposta,
            titulo=titulo,
            anexos_adicionados=attachment_names_uploaded,
            link_pasta_sharepoint=web_url,
        )

        return {
            "work_item_id": work_item_id,
            "folder_id": folder_id,
            "web_url": web_url,
            "attachments_synced": attachments_synced,
            "attachment_names": attachment_names_uploaded,
            "cliente": client_name,
            "titulo": titulo,
            "numero_proposta": numero_proposta,
        }
