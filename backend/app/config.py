"""Configurações do sistema usando Pydantic Settings."""
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent.parent
_ENV_FILE = _BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """Configurações da aplicação com validação automática."""

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE if _ENV_FILE.exists() else ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Azure DevOps
    AZURE_DEVOPS_ORG: str = Field(
        default="qualiit",
        description="Organização do Azure DevOps",
    )
    AZURE_DEVOPS_PROJECT: str = Field(
        default="Quali IT - Inovação e Tecnologia",
        description="Nome do projeto no Azure DevOps",
    )
    AZURE_DEVOPS_PAT: str = Field(
        default="",
        description="Personal Access Token do Azure DevOps (obrigatório via env var)",
    )

    @field_validator("AZURE_DEVOPS_ORG", mode="before")
    @classmethod
    def parse_azure_devops_org(cls, v: str) -> str:
        """Trata variáveis não definidas do Azure DevOps Pipeline."""
        if isinstance(v, str) and v.startswith("$(") and v.endswith(")"):
            return "qualiit"
        return v

    # SharePoint / Microsoft Graph
    SHAREPOINT_CLIENT_ID: str = Field(
        default="",
        description="Client ID (Application ID) do Microsoft Entra ID para SharePoint",
    )
    SHAREPOINT_CLIENT_SECRET: str = Field(
        default="",
        description="Client Secret do Microsoft Entra ID (obrigatório se usar SharePoint)",
    )
    SHAREPOINT_TENANT_ID: str = Field(
        default="",
        description="Tenant ID (Directory ID) do Microsoft Entra ID",
    )
    SHAREPOINT_SITE_URL: str = Field(
        default="",
        description="URL do site SharePoint (ex: https://qualiitcombr.sharepoint.com/sites/projetosqualiit)",
    )
    SHAREPOINT_FOLDER_PATH_BASE: str = Field(
        default="Documentos Compartilhados/Projetos DevOps",
        description="Caminho base da biblioteca no SharePoint (Ano/Cliente/Feature... criados abaixo)",
    )

    # Webhook (Service Hooks Azure DevOps → FastAPI)
    WEBHOOK_SECRET: str = Field(
        default="",
        description="Secret para validar requisições do Service Hook (header X-Webhook-Secret ou similar)",
    )

    # Logging
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    # Pipeline: varredura incremental (após primeira execução, só processa Features novas/alteradas)
    PIPELINE_FULL_SCAN: bool = Field(
        default=False,
        description="Se True (1/true/yes), ignora last_run e faz varredura completa. Use na 1ª execução ou para reparo.",
    )

    # Opcional: pasta OneDrive para arquivos de fechamento
    CLOSED_FEATURES_ONEDRIVE_PATH: str = Field(
        default="",
        description="Caminho ou URL da pasta ClosedFeatures no OneDrive (opcional)",
    )

    @property
    def azure_devops_base_url(self) -> str:
        """URL base do Azure DevOps."""
        return f"https://dev.azure.com/{self.AZURE_DEVOPS_ORG}"

    def validate_pat(self) -> None:
        """Valida que o PAT foi fornecido. Chame antes de usar."""
        if not self.AZURE_DEVOPS_PAT or self.AZURE_DEVOPS_PAT.strip() == "":
            raise ValueError("AZURE_DEVOPS_PAT deve ser configurado via variável de ambiente")


settings = Settings()
