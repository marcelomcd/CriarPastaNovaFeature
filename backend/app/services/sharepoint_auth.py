"""Serviço de autenticação SharePoint usando OAuth2 (Microsoft Entra ID)."""
import logging
from datetime import datetime, timedelta
from typing import Optional

from msal import ConfidentialClientApplication

from app.config import settings

logger = logging.getLogger(__name__)


class SharePointAuthService:
    """Gerencia autenticação OAuth2 para SharePoint (Microsoft Graph)."""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> None:
        if not (client_id or settings.SHAREPOINT_CLIENT_ID):
            raise ValueError("SHAREPOINT_CLIENT_ID não configurado")
        if not (client_secret or settings.SHAREPOINT_CLIENT_SECRET):
            raise ValueError("SHAREPOINT_CLIENT_SECRET não configurado")
        if not (tenant_id or settings.SHAREPOINT_TENANT_ID):
            raise ValueError("SHAREPOINT_TENANT_ID não configurado")

        self.client_id = client_id or settings.SHAREPOINT_CLIENT_ID
        self.client_secret = client_secret or settings.SHAREPOINT_CLIENT_SECRET
        self.tenant_id = tenant_id or settings.SHAREPOINT_TENANT_ID
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scope = ["https://graph.microsoft.com/.default"]
        self.app = ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=self.authority,
        )
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    def get_access_token(self, force_refresh: bool = False) -> str:
        """Obtém access token válido (usa cache se disponível)."""
        if (
            not force_refresh
            and self._access_token
            and self._token_expires_at
            and datetime.now() < (self._token_expires_at - timedelta(minutes=5))
        ):
            return self._access_token

        result = self.app.acquire_token_for_client(scopes=self.scope)
        if "access_token" not in result:
            err = result.get("error_description", result.get("error", "Erro desconhecido"))
            raise ValueError(f"Falha na autenticação: {err}")

        self._access_token = result["access_token"]
        expires_in = result.get("expires_in", 3600)
        self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
        return self._access_token

    def clear_token_cache(self) -> None:
        """Limpa cache de token."""
        self._access_token = None
        self._token_expires_at = None
