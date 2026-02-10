"""
Script de varredura: lista todas as Features (Azure DevOps) e para cada uma
garante pasta no SharePoint, link em Custom.LinkPastaDocumentacao e sincronização de anexos.
Executado pela pipeline agendada (azure-pipelines.yml).
"""
import logging
import sys
from pathlib import Path

# Garante que o backend/app está no path quando rodado como script
_backend = Path(__file__).resolve().parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from app.config import settings
from app.services.feature_folder_service import FeatureFolderService

logging.basicConfig(
    level=getattr(logging, (settings.LOG_LEVEL or "INFO").upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> int:
    settings.validate_pat()
    svc = FeatureFolderService()
    features = svc.devops.list_features(include_closed=True)
    logger.info("Varredura: %s Feature(s) encontrada(s)", len(features))
    ok = 0
    err = 0
    for wi in features:
        try:
            svc.process_feature(wi.id)
            ok += 1
        except Exception as e:
            logger.exception("Feature %s: %s", wi.id, e)
            err += 1
    logger.info("Varredura concluída: %s ok, %s erro(s)", ok, err)
    return 0 if err == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
