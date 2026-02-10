"""Configuração pytest e fixtures."""
import sys
from pathlib import Path

import pytest

# Garante que backend está no path
_backend = Path(__file__).resolve().parent.parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))


def pytest_configure(config):
    config.addinivalue_line("markers", "integration: testes que exigem .env (SharePoint, Azure DevOps)")


def pytest_collection_modifyitems(config, items):
    for item in items:
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
