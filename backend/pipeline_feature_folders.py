"""
Script de varredura: lista Features (Azure DevOps) e para cada uma garante pasta no SharePoint,
link em Custom.LinkPastaDocumentacao e sincronização de anexos.

Modo de atualização (não recria tudo):
- Pastas: só são criadas se ainda não existirem para aquela Feature.
- Anexos: só são enviados os que ainda não estão na pasta (evita duplicar).
- Link: atualizado no work item apenas se estiver diferente.

Após a primeira execução, a varredura é incremental (só Features novas ou alteradas).
Para processar todas as Features de novo (preencher lacunas), use PIPELINE_FULL_SCAN=1.
Log em HTML: backend/logs/pipeline_YYYYMMDD_HHMMSS.html (publicado como artefato).
"""
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# Garante que o backend/app está no path quando rodado como script
_backend = Path(__file__).resolve().parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from app.config import settings
from app.services.feature_folder_service import (
    FeatureFolderService,
    work_item_to_feature_info,
    feature_info_to_folder_path,
)
from app.utils.pipeline_logger import log_feature_result, start_html_log, end_html_log

logging.basicConfig(
    level=getattr(logging, (settings.LOG_LEVEL or "INFO").upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

LOGS_DIR = _backend / "logs"
LAST_RUN_FILE = LOGS_DIR / "last_run.txt"


def _read_last_run() -> datetime | None:
    """Retorna a data/hora da última execução (UTC) ou None se não existir."""
    if not LAST_RUN_FILE.exists():
        return None
    try:
        text = LAST_RUN_FILE.read_text(encoding="utf-8").strip()
        if not text:
            return None
        # Aceita ISO com Z ou +00:00
        s = text.replace("Z", "+00:00")
        return datetime.fromisoformat(s)
    except (ValueError, OSError):
        return None


def _write_last_run() -> None:
    """Registra a data/hora desta execução (UTC) para a próxima varredura incremental."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        LAST_RUN_FILE.write_text(now, encoding="utf-8")
    except OSError as e:
        logger.warning("Não foi possível gravar last_run: %s", e)


def main() -> int:
    settings.validate_pat()
    start_html_log()
    try:
        svc = FeatureFolderService()
        use_incremental = not settings.PIPELINE_FULL_SCAN
        updated_since = _read_last_run() if use_incremental else None
        if updated_since:
            features = svc.devops.list_features(include_closed=True, updated_since=updated_since)
            logger.info("Varredura incremental (desde %s): %s Feature(s) encontrada(s)", updated_since.isoformat(), len(features))
        else:
            features = svc.devops.list_features(include_closed=True)
            logger.info("Varredura completa: %s Feature(s) encontrada(s)", len(features))
        ok = 0
        err = 0
        failed_ids: list[int] = []
        for wi in features:
            try:
                svc.process_feature(wi.id)
                ok += 1
            except Exception as e:
                logger.exception("Feature %s: %s", wi.id, e)
                err += 1
                failed_ids.append(wi.id)
                try:
                    info = work_item_to_feature_info(wi)
                    path = feature_info_to_folder_path(info)
                    log_feature_result(
                        work_item_id=wi.id,
                        cliente=path.client_name,
                        numero_proposta=info.numero_proposta,
                        titulo=info.title,
                        anexos_adicionados=[],
                        link_pasta_sharepoint="—",
                        erro=str(e),
                    )
                except Exception as log_ex:
                    logger.warning("Feature %s: não foi possível registrar no log HTML: %s", wi.id, log_ex)
        if failed_ids:
            logger.info("Segundo passo: reprocessando %s item(ns) com falha (apenas pasta e anexos, sem atualizar work item)", len(failed_ids))
            retry_ok = 0
            retry_err = 0
            for wi_id in failed_ids:
                try:
                    svc.process_feature(wi_id, skip_work_item_update=True)
                    retry_ok += 1
                except Exception as e:
                    logger.exception("Feature %s (retry): %s", wi_id, e)
                    retry_err += 1
            logger.info("Retry: %s ok, %s erro(s)", retry_ok, retry_err)
            ok += retry_ok
            err = retry_err
        logger.info("Varredura concluída: %s ok, %s erro(s)", ok, err)
        _write_last_run()
        # Com PIPELINE_FAIL_ON_FEATURE_ERROR=False (default), o passo não falha quando há erros em Features (relatório HTML tem o detalhe).
        return 0 if (err == 0 or not settings.PIPELINE_FAIL_ON_FEATURE_ERROR) else 1
    finally:
        end_html_log()


if __name__ == "__main__":
    sys.exit(main())
