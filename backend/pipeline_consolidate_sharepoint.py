"""
Script para consolidar documentos de várias pastas do SharePoint (URLs de compartilhamento)
na pasta base do projeto, preservando a mesma estrutura:

  Documentações de Projetos > Projetos DevOps > Ano > Cliente > Feature ID - Nº Proposta - Título

- Não duplica arquivos: se o arquivo já existir na pasta de destino, é ignorado.
- Não usa prefixos: nomes de arquivo e estrutura de pastas são mantidos.

Variável obrigatória: SHAREPOINT_SOURCE_FOLDER_URLS — URLs separadas por ponto e vírgula (;).
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


def main() -> int:
    urls_raw = os.environ.get("SHAREPOINT_SOURCE_FOLDER_URLS", "").strip()
    if not urls_raw:
        logger.error("SHAREPOINT_SOURCE_FOLDER_URLS não definida. Use URLs de pasta separadas por ;")
        return 1
    urls = [u.strip() for u in urls_raw.split(";") if u.strip()]
    if not urls:
        logger.error("Nenhuma URL válida em SHAREPOINT_SOURCE_FOLDER_URLS")
        return 1
    logger.info("Consolidando %s pasta(s) em Projetos DevOps (mesma estrutura, sem duplicar).", len(urls))
    sp = SharePointFileService()
    total_copied = 0
    total_skipped = 0
    errors = 0
    for i, sharing_url in enumerate(urls):
        try:
            item = sp.get_drive_item_by_sharing_url(sharing_url)
            if not item.get("folder"):
                logger.warning("URL %s não é uma pasta, ignorando.", i + 1)
                continue
            fid, did, name = item["id"], item["driveId"], item.get("name") or "pasta"
            logger.info("Origem %s: %s", i + 1, name)
            for file_id, file_name, rel_path in sp.list_files_recursive(did, fid):
                folder_rel = str(Path(rel_path).parent).replace("\\", "/").strip()
                if folder_rel in (".", ""):
                    folder_rel = ""
                upload_name = sanitize_attachment_filename(file_name) or file_name
                try:
                    drive_id, folder_id = sp.ensure_folder_path(folder_rel)
                    existing = {it.get("name") or "" for it in sp.list_folder_children(drive_id, folder_id) if it.get("name")}
                    if upload_name in existing:
                        logger.debug("  Já existe, ignorando: %s", upload_name)
                        total_skipped += 1
                        continue
                    content = sp.download_item_content(did, file_id)
                    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_name).suffix or "") as tmp:
                        tmp.write(content)
                        tmp.flush()
                        tmp_path = Path(tmp.name)
                    try:
                        sp.upload_file(
                            tmp_path,
                            folder_id=folder_id,
                            drive_id=drive_id,
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
        except Exception as e:
            errors += 1
            logger.exception("Erro ao processar URL %s: %s", i + 1, e)
    logger.info("Consolidação concluída: %s copiados, %s já existiam (ignorados), %s erro(s).", total_copied, total_skipped, errors)
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
