"""Modelos para integração Azure DevOps (work items, resposta da API)."""
from typing import Any, Optional

from pydantic import BaseModel


class WorkItemResponse(BaseModel):
    """Resposta de um Work Item do Azure DevOps."""

    id: int
    rev: int
    fields: dict[str, Any]
    relations: Optional[list[dict[str, Any]]] = None
    url: str = ""


# Nome do campo customizado no Azure DevOps para o link da pasta
LINK_PASTA_DOCUMENTACAO_FIELD = "Custom.LinkPastaDocumentacao"
