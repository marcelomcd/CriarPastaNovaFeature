"""FastAPI app: webhook Azure DevOps, health e sync manual por Feature."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.services.feature_folder_service import FeatureFolderService

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # cleanup if needed
    pass


app = FastAPI(title="FluxoNovasFeatures", description="Webhook e sync pastas SharePoint por Feature", lifespan=lifespan)


def _get_feature_id_from_payload(body: dict) -> int | None:
    """Extrai work item id do payload do Service Hook. Valida que é Feature."""
    resource = body.get("resource") or {}
    wi_type = (resource.get("fields") or {}).get("System.WorkItemType") or resource.get("workItemType") or ""
    if "Feature" not in wi_type:
        return None
    return resource.get("id")


@app.post("/webhook/devops")
async def webhook_devops(
    body: dict,
    x_webhook_secret: str | None = Header(None, alias="X-Webhook-Secret"),
):
    """
    Recebe POST do Azure DevOps Service Hook (work item created / work item updated).
    Valida secret e processa a Feature (pasta, link, anexos).
    """
    if settings.WEBHOOK_SECRET and (not x_webhook_secret or x_webhook_secret != settings.WEBHOOK_SECRET):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Webhook secret inválido")
    feature_id = _get_feature_id_from_payload(body)
    if feature_id is None:
        return JSONResponse(content={"ok": True, "message": "Ignorado (não é Feature)"}, status_code=200)
    try:
        settings.validate_pat()
        svc = FeatureFolderService()
        result = svc.process_feature(feature_id)
        return JSONResponse(content={"ok": True, "result": result}, status_code=200)
    except Exception as e:
        logger.exception("Erro ao processar Feature %s", feature_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.get("/health")
async def health():
    """Health check para monitoramento e deploy."""
    return {"status": "ok"}


@app.post("/sync/feature/{feature_id:int}")
async def sync_feature(feature_id: int):
    """Disparo manual: processa uma Feature por ID (pasta, link, anexos)."""
    try:
        settings.validate_pat()
        svc = FeatureFolderService()
        result = svc.process_feature(feature_id)
        return {"ok": True, "result": result}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.exception("Erro ao processar Feature %s", feature_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
