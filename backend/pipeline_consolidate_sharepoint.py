"""
Script para consolidar documentos de várias pastas do SharePoint na pasta base do projeto
(Projetos DevOps), preservando a estrutura Ano > Cliente > Feature ID - Nº Proposta - Título.

- Não duplica arquivos nem pastas: arquivo existente é ignorado; pastas reutilizadas.
- Estrutura unificada por Feature ID (mesmo projeto vai para a mesma pasta).

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
from app.services.sharepoint_files import SharePointFileService
from app.utils.name_utils import sanitize_attachment_filename

logging.basicConfig(
    level=getattr(logging, (settings.LOG_LEVEL or "INFO").upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _copy_from_folder(sp: SharePointFileService, drive_id: str, folder_id: str, source_name: str) -> tuple[int, int, int]:
    """Copia todos os arquivos de uma pasta (recursivo) para o destino (base), preservando estrutura. Retorna (copied, skipped, errors)."""
    total_copied = 0
    total_skipped = 0
    errors = 0
    for file_id, file_name, rel_path in sp.list_files_recursive(drive_id, folder_id):
        folder_rel = str(Path(rel_path).parent).replace("\\", "/").strip()
        if folder_rel in (".", ""):
            folder_rel = ""
        upload_name = sanitize_attachment_filename(file_name) or file_name
        try:
            dest_drive_id, dest_folder_id = sp.ensure_folder_path(folder_rel)
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
                logger.info("  Copiado: %s", f"{folder_rel}/{upload_name}" if folder_rel else upload_name)
            finally:
                try:
                    tmp_path.unlink(missing_ok=True)
                except OSError:
                    pass
        except Exception as e:
            errors += 1
            logger.warning("  Erro ao copiar %s: %s", rel_path, e)
    return total_copied, total_skipped, errors


def main() -> int:
    paths_raw = os.environ.get("SHAREPOINT_SOURCE_FOLDER_PATHS", "").strip()
    urls_raw = os.environ.get("SHAREPOINT_SOURCE_FOLDER_URLS", "").strip()
    paths = [p.strip() for p in paths_raw.split(";") if p.strip()]
    urls = [u.strip() for u in urls_raw.split(";") if u.strip()]
    if not paths and not urls:
        logger.error(
            "Defina SHAREPOINT_SOURCE_FOLDER_PATHS (caminhos na biblioteca, ex: Documentação dos Clientes;Projetos DevOps OLD) "
            "ou SHAREPOINT_SOURCE_FOLDER_URLS (links de compartilhamento)"
        )
        return 1
    logger.info(
        "Consolidando em Projetos DevOps (estrutura Ano > Cliente > Feature...; sem duplicar; Feature ID como base)."
    )
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
                logger.info("Origem (path) %s: %s", i + 1, folder_path)
                c, s, e = _copy_from_folder(sp, drive_id, fid, folder_path)
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
            logger.info("Origem (URL) %s: %s", i + 1, name)
            c, s, e = _copy_from_folder(sp, did, fid, name)
            total_copied += c
            total_skipped += s
            errors += e
        except Exception as e:
            errors += 1
            logger.exception("Erro ao processar URL %s: %s", i + 1, e)
    logger.info("Consolidação concluída: %s copiados, %s já existiam (ignorados), %s erro(s).", total_copied, total_skipped, errors)
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
