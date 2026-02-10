"""Orquestração: por Feature, criar pasta no SharePoint, link e sincronizar anexos."""
import logging
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


def feature_info_to_folder_path(info: FeatureInfo) -> FeatureFolderPath:
    """Converte FeatureInfo em FeatureFolderPath (nome da pasta e cliente normalizados)."""
    client_name = normalize_client_name(info.area_path.split("\\")[-1] if info.area_path else "")
    folder_name = build_feature_folder_name(
        info.id,
        info.numero_proposta,
        info.title,
    )
    return FeatureFolderPath(year=info.year, client_name=client_name, folder_name=folder_name)


class FeatureFolderService:
    """Orquestra criação de pasta no SharePoint, link e sincronização de anexos por Feature."""

    def __init__(
        self,
        devops_client: AzureDevOpsClient | None = None,
        sharepoint_service: SharePointFileService | None = None,
    ) -> None:
        self.devops = devops_client or AzureDevOpsClient()
        self.sharepoint = sharepoint_service or SharePointFileService()

    def process_feature(self, work_item_id: int) -> dict:
        """
        Para uma Feature: garante pasta no SharePoint, link e anexos.
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
        web_url = self.sharepoint.create_sharing_link(drive_id, folder_id)

        current_link = (wi.fields.get("Custom.LinkPastaDocumentacao") or "").strip()
        if current_link != web_url:
            self.devops.update_work_item_link_pasta(work_item_id, web_url)
            logger.info("Atualizado Custom.LinkPastaDocumentacao para Feature %s", work_item_id)

        attachments_synced = 0
        for att_id, name in self.devops.list_attachment_relations(wi):
            try:
                tmp = self.devops.download_attachment(att_id, file_name=name)
                try:
                    self.sharepoint.upload_file(tmp, folder_id=folder_id, drive_id=drive_id, overwrite=True)
                    attachments_synced += 1
                finally:
                    try:
                        tmp.unlink(missing_ok=True)
                    except OSError:
                        pass
            except Exception as e:
                logger.warning("Falha ao sincronizar anexo %s da Feature %s: %s", att_id, work_item_id, e)

        return {
            "work_item_id": work_item_id,
            "folder_id": folder_id,
            "web_url": web_url,
            "attachments_synced": attachments_synced,
        }
