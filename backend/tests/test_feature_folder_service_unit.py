"""Testes unitários do feature_folder_service com mocks."""
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.models.devops_models import WorkItemResponse
from app.services.feature_folder_service import (
    work_item_to_feature_info,
    feature_info_to_folder_path,
    _parse_created_date,
)


def test_parse_created_date_iso_string():
    fields = {"System.CreatedDate": "2025-02-10T14:30:00Z"}
    dt = _parse_created_date(fields)
    assert dt.year == 2025
    assert dt.month == 2
    assert dt.day == 10


def test_parse_created_date_missing_returns_now():
    dt = _parse_created_date({})
    assert dt is not None


def test_work_item_to_feature_info():
    wi = WorkItemResponse(
        id=100,
        rev=1,
        fields={
            "System.Title": "Minha Feature",
            "System.AreaPath": "Org\\Projeto\\Cliente\\CAMIL ALIMENTOS",
            "System.CreatedDate": "2025-01-15T10:00:00Z",
            "System.State": "Active",
            "Custom.NumeroProposta": "P001",
            "Custom.LinkPastaDocumentacao": None,
        },
        relations=None,
        url="",
    )
    info = work_item_to_feature_info(wi)
    assert info.id == 100
    assert info.title == "Minha Feature"
    assert info.area_path == "Org\\Projeto\\Cliente\\CAMIL ALIMENTOS"
    assert info.state == "Active"
    assert info.numero_proposta == "P001"
    assert info.year == 2025


def test_feature_info_to_folder_path():
    from app.models.feature_folder import FeatureInfo
    info = FeatureInfo(
        id=100,
        title="Titulo da Feature",
        area_path="A\\B\\CAMIL ALIMENTOS",
        created_date=datetime(2025, 1, 1),
        state="Active",
        numero_proposta="P001",
        link_pasta_documentacao=None,
    )
    path = feature_info_to_folder_path(info)
    assert path.year == 2025
    assert "Camil" in path.client_name
    assert "100" in path.folder_name
    assert path.relative_path().startswith("2025/")
