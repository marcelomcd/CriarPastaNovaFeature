"""Testes para modelos feature_folder."""
from datetime import datetime

import pytest

from app.models.feature_folder import FeatureInfo, FeatureFolderPath


def test_feature_info_year():
    info = FeatureInfo(
        id=1,
        title="T",
        area_path="A\\B\\Cliente",
        created_date=datetime(2025, 3, 15),
        state="Active",
        numero_proposta="P001",
        link_pasta_documentacao=None,
    )
    assert info.year == 2025


def test_feature_folder_path_relative_path():
    path = FeatureFolderPath(year=2025, client_name="Camil Alimentos", folder_name="1 - N/A - Titulo")
    assert path.relative_path() == "2025/Camil Alimentos/1 - N/A - Titulo"
