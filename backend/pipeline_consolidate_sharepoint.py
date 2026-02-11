"""
Script para consolidar documentos de várias pastas do SharePoint na pasta base do projeto
(Projetos DevOps), preservando a estrutura Ano > Cliente > Feature ID - Nº Proposta - Título.

- Não duplica arquivos nem pastas: arquivo existente é ignorado; pastas reutilizadas.
- Apenas arquivos válidos: ignora pastas/arquivos de metadados e sistema (ex.: .metadata, .plugins,
  .root, .indexes, history.version, properties.index, properties.version, desktop.ini, etc.).
- Estrutura unificada por Feature: pastas de origem são mapeadas por Feature ID, Número da Proposta ou Título (Azure DevOps).
- Ao final, verifica se as pastas em Projetos DevOps estão no padrão canônico.

Origens (uma das duas variáveis obrigatórias):
- SHAREPOINT_SOURCE_FOLDER_PATHS — caminhos relativos à biblioteca, separados por ; (ex.: Documentação dos Clientes;Projetos DevOps OLD)
- SHAREPOINT_SOURCE_FOLDER_URLS — URLs de compartilhamento (/:f:/s/...?e=xxx), separadas por ;
"""
import logging
import os
import sys
import tempfile
from pathlib import Path

_backend = Path(__file__).resolve().parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from app.config import settings
from app.services.devops_client import AzureDevOpsClient
from app.services.feature_folder_service import work_item_to_feature_info, feature_info_to_folder_path
from app.services.sharepoint_files import SharePointFileService
from app.utils.name_utils import sanitize_attachment_filename, normalize_client_name, is_canonical_feature_folder_name

logging.basicConfig(
    level=getattr(logging, (settings.LOG_LEVEL or "INFO").upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Segmentos de caminho que indicam pastas internas/metadados (não copiar)
EXCLUDED_PATH_SEGMENTS = frozenset({
    ".metadata", ".plugins", ".root", ".indexes",
    "node_modules", ".git", ".vs", ".idea", "obj", "bin",
})
# Arquivos conhecidos de metadados/sistema (SharePoint, Eclipse, etc.)
EXCLUDED_FILE_NAMES = frozenset({
    "history.version", "properties.index", "properties.version",
    "desktop.ini", "thumbs.db", ".ds_store",
})


def _is_valid_file_for_consolidation(rel_path: str, file_name: str) -> bool:
    """
    Retorna False se o arquivo estiver em pasta de metadados/oculta ou for arquivo de sistema,
    para não copiar dados internos do SharePoint ou de IDEs.
    """
    path_str = (rel_path or "").replace("\\", "/").strip()
    if not path_str and not file_name:
        return False
    segments = [p.strip() for p in path_str.split("/") if p.strip()]
    for seg in segments:
        if seg in EXCLUDED_PATH_SEGMENTS:
            return False
        if seg.startswith("."):
            return False
    name = (file_name or "").strip().lower()
    if name in EXCLUDED_FILE_NAMES:
        return False
    if name.startswith("."):
        return False
    return True


def _parse_source_folder_path(folder_rel: str) -> tuple[int | None, str | None, str | None]:
    """
    Extrai (ano, cliente, nome_pasta) do caminho relativo da origem.
    Ex.: "2024/Cliente X/Pasta" -> (2024, "Cliente X", "Pasta")
         "2024/Closed/Cliente X/Pasta" -> (2024, "Cliente X", "Pasta")
    Retorna (None, None, None) se não houver pelo menos 3 segmentos utilizáveis.
    """
    parts = [p for p in folder_rel.replace("\\", "/").strip("/").split("/") if p.strip()]
    if len(parts) < 3:
        return (None, None, None)
    year = None
    if parts[0].isdigit() and len(parts[0]) == 4:
        year = int(parts[0])
    if len(parts) == 3:
        return (year, parts[1], parts[2])
    if len(parts) >= 4 and parts[1].strip().lower() == "closed":
        return (year, parts[2], parts[3])
    return (year, parts[1], parts[2])


def _resolve_canonical_path(
    folder_rel: str, devops: AzureDevOpsClient | None
) -> str:
    """
    Se o caminho da origem tiver ano/cliente/nome_pasta e o Azure DevOps resolver a Feature
    (por ID, Número da Proposta ou Título), retorna o caminho canônico no padrão
    Projetos DevOps > Ano > Cliente > Feature ID - Nº Proposta - Título.
    Caso contrário retorna folder_rel (estrutura original).
    """
    if not devops:
        return folder_rel
    year, client_raw, folder_name = _parse_source_folder_path(folder_rel)
    if not folder_name:
        return folder_rel
    client_norm = normalize_client_name(client_raw) if client_raw else None
    try:
        wi = devops.resolve_feature_for_folder_name(folder_name, client_norm)
        if not wi:
            return folder_rel
        info = work_item_to_feature_info(wi)
        path = feature_info_to_folder_path(info)
        return path.relative_path()
    except Exception as e:
        logger.debug("Não foi possível resolver Feature para pasta %s: %s", folder_name, e)
        return folder_rel


def _copy_from_folder(
    sp: SharePointFileService,
    drive_id: str,
    folder_id: str,
    source_name: str,
    devops: AzureDevOpsClient | None,
) -> tuple[int, int, int]:
    """Copia todos os arquivos de uma pasta (recursivo) para o destino (base), usando caminho canônico quando possível. Retorna (copied, skipped, errors)."""
    total_copied = 0
    total_skipped = 0
    errors = 0
    processed = 0
    for file_id, file_name, rel_path in sp.list_files_recursive(drive_id, folder_id):
        processed += 1
        if not _is_valid_file_for_consolidation(rel_path, file_name):
            logger.debug("  Ignorando arquivo de metadados/sistema: %s", rel_path or file_name)
            total_skipped += 1
            continue
        if processed % 15 == 0 or processed == 1:
            logger.info("  ... %s arquivo(s) processado(s) até agora (%s copiados, %s ignorados)", processed, total_copied, total_skipped)
        folder_rel = str(Path(rel_path).parent).replace("\\", "/").strip()
        if folder_rel in (".", ""):
            folder_rel = ""
        dest_rel = _resolve_canonical_path(folder_rel, devops)
        upload_name = sanitize_attachment_filename(file_name) or file_name
        try:
            dest_drive_id, dest_folder_id = sp.ensure_folder_path(dest_rel)
            existing = {it.get("name") or "" for it in sp.list_folder_children(dest_drive_id, dest_folder_id) if it.get("name")}
            if upload_name in existing:
                logger.debug("  Já existe, ignorando: %s", upload_name)
                total_skipped += 1
                continue
            content = sp.download_item_content(drive_id, file_id)
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_name).suffix or "") as tmp:
                tmp.write(content)
                tmp.flush()
                tmp_path = Path(tmp.name)
            try:
                sp.upload_file(
                    tmp_path,
                    folder_id=dest_folder_id,
                    drive_id=dest_drive_id,
                    overwrite=False,
                    upload_name=upload_name,
                )
                total_copied += 1
                logger.info("  Copiado: %s", f"{dest_rel}/{upload_name}" if dest_rel else upload_name)
            finally:
                try:
                    tmp_path.unlink(missing_ok=True)
                except OSError:
                    pass
        except Exception as e:
            errors += 1
            logger.warning("  Erro ao copiar %s: %s", rel_path, e)
    logger.info("  Pasta concluída: %s processados, %s copiados, %s ignorados, %s erro(s).", processed, total_copied, total_skipped, errors)
    return total_copied, total_skipped, errors


def _verify_projetos_devops_structure(sp: SharePointFileService) -> list[str]:
    """
    Lista o conteúdo da pasta Projetos DevOps e identifica pastas de Feature (Ano/Cliente/NomePasta
    ou Ano/Closed/Cliente/NomePasta) cujo nome não segue o padrão: ID - Nº Proposta - Título.
    Retorna lista de caminhos relativos fora do padrão.
    """
    out_of_pattern: list[str] = []
    try:
        dest_drive_id, dest_base_id = sp.ensure_folder_path("")
    except Exception as e:
        logger.warning("Não foi possível acessar pasta Projetos DevOps para verificação: %s", e)
        return out_of_pattern
    seen_folders: set[str] = set()
    for _file_id, _name, rel_path in sp.list_files_recursive(dest_drive_id, dest_base_id):
        folder_rel = str(Path(rel_path).parent).replace("\\", "/").strip()
        if not folder_rel or folder_rel in seen_folders:
            continue
        seen_folders.add(folder_rel)
        parts = [p for p in folder_rel.replace("\\", "/").split("/") if p.strip()]
        if len(parts) < 3:
            continue
        # Pasta de Feature é o último segmento (sob Ano/Cliente ou Ano/Closed/Cliente)
        feature_folder_name = parts[-1]
        if not is_canonical_feature_folder_name(feature_folder_name):
            out_of_pattern.append(folder_rel)
    return sorted(out_of_pattern)


def main() -> int:
    paths_raw = (settings.SHAREPOINT_SOURCE_FOLDER_PATHS or os.environ.get("SHAREPOINT_SOURCE_FOLDER_PATHS", "")).strip()
    urls_raw = (settings.SHAREPOINT_SOURCE_FOLDER_URLS or os.environ.get("SHAREPOINT_SOURCE_FOLDER_URLS", "")).strip()
    paths = [p.strip() for p in paths_raw.split(";") if p.strip()]
    urls = [u.strip() for u in urls_raw.split(";") if u.strip()]
    if not paths and not urls:
        logger.error(
            "Defina SHAREPOINT_SOURCE_FOLDER_PATHS (caminhos na biblioteca, ex: Documentação dos Clientes;Projetos DevOps OLD) "
            "ou SHAREPOINT_SOURCE_FOLDER_URLS (links de compartilhamento)"
        )
        return 1
    logger.info(
        "Consolidando em Projetos DevOps (estrutura Ano > Cliente > Feature ID - Nº Proposta - Título; resolução por ID/Proposta/Título no Azure DevOps)."
    )
    devops: AzureDevOpsClient | None = None
    try:
        if getattr(settings, "AZURE_DEVOPS_PAT", None) and (settings.AZURE_DEVOPS_PAT or "").strip() not in ("", "SEU_PAT_AQUI"):
            devops = AzureDevOpsClient()
            logger.info("Azure DevOps conectado: pastas de origem serão mapeadas para o padrão canônico quando possível.")
    except Exception as e:
        logger.warning("Azure DevOps não disponível (consolidação manterá estrutura de origem): %s", e)
    sp = SharePointFileService()
    site_id = sp._get_site_id()
    drive_id = sp._get_drive_id(site_id)
    total_copied = 0
    total_skipped = 0
    errors = 0

    if paths:
        for i, folder_path in enumerate(paths):
            try:
                fid = sp._get_folder_id(drive_id, folder_path)
                if not fid:
                    logger.warning("Pasta de origem não encontrada: %s", folder_path)
                    errors += 1
                    continue
                logger.info("Origem (path) %s/%s: %s", i + 1, len(paths), folder_path)
                c, s, e = _copy_from_folder(sp, drive_id, fid, folder_path, devops)
                total_copied += c
                total_skipped += s
                errors += e
            except Exception as ex:
                errors += 1
                logger.exception("Erro ao processar path %s: %s", folder_path, ex)

    for i, sharing_url in enumerate(urls):
        try:
            item = sp.get_drive_item_by_sharing_url(sharing_url)
            if not item.get("folder"):
                logger.warning("URL %s não é uma pasta, ignorando.", i + 1)
                continue
            fid, did, name = item["id"], item["driveId"], item.get("name") or "pasta"
            logger.info("Origem (URL) %s/%s: %s", i + 1, len(urls), name)
            c, s, e = _copy_from_folder(sp, did, fid, name, devops)
            total_copied += c
            total_skipped += s
            errors += e
        except Exception as e:
            errors += 1
            logger.exception("Erro ao processar URL %s: %s", i + 1, e)

    logger.info("Consolidação concluída: %s copiados, %s já existiam (ignorados), %s erro(s).", total_copied, total_skipped, errors)

    # Verificação final: pastas em Projetos DevOps fora do padrão canônico
    out_of_pattern = _verify_projetos_devops_structure(sp)
    if out_of_pattern:
        logger.warning(
            "Verificação do padrão em Projetos DevOps: %s pasta(s) fora do padrão (ID - Nº Proposta - Título): %s",
            len(out_of_pattern),
            out_of_pattern[:20] if len(out_of_pattern) > 20 else out_of_pattern,
        )
        if len(out_of_pattern) > 20:
            logger.warning("  ... e mais %s pasta(s). Revise manualmente se desejar alinhar ao padrão.", len(out_of_pattern) - 20)
    else:
        logger.info("Verificação do padrão: pastas em Projetos DevOps estão no padrão Ano > Cliente > Feature ID - Nº Proposta - Título.")

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
