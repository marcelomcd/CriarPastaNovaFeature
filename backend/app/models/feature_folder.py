"""Modelos para estrutura de pastas por Feature no SharePoint."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class FeatureInfo:
    """Dados da Feature extraídos do Azure DevOps."""

    id: int
    title: str
    area_path: str
    created_date: datetime
    state: str
    numero_proposta: Optional[str]
    link_pasta_documentacao: Optional[str]

    @property
    def year(self) -> int:
        """Ano de criação da Feature."""
        return self.created_date.year


@dataclass(frozen=True)
class FeatureFolderPath:
    """Caminho da pasta da Feature no SharePoint (relativo à base)."""

    year: int
    client_name: str  # normalizado (ex.: Camil Alimentos)
    folder_name: str  # ex.: "12345 - N/A - Título da Feature"
    closed: bool = False  # se True, pasta fica em Ano/Closed/Cliente/NomePasta

    def relative_path(self) -> str:
        """Caminho relativo: Ano/Cliente/NomePasta ou Ano/Closed/Cliente/NomePasta."""
        if self.closed:
            return f"{self.year}/Closed/{self.client_name}/{self.folder_name}"
        return f"{self.year}/{self.client_name}/{self.folder_name}"

    def relative_path_active(self) -> str:
        """Caminho ativo (sem Closed): Ano/Cliente/NomePasta. Usado para mover para Closed."""
        return f"{self.year}/{self.client_name}/{self.folder_name}"
