"""
Testes de integração: leitura/escrita no SharePoint.
Requer .env preenchido (SHAREPOINT_*). Execute com: pytest -m integration
"""
import os
import tempfile
from pathlib import Path

import pytest

pytest.importorskip("app")  # garante que app está no path


@pytest.mark.integration
class TestSharePointIntegration:
    """Testes de integração com SharePoint (cria pasta de teste, upload, link, limpeza)."""

    @pytest.fixture(scope="class")
    def env_ok(self):
        """Só roda se variáveis SharePoint estiverem configuradas (via .env)."""
        from app.config import settings
        if not (settings.SHAREPOINT_CLIENT_ID and settings.SHAREPOINT_CLIENT_SECRET
                and settings.SHAREPOINT_TENANT_ID and settings.SHAREPOINT_SITE_URL):
            pytest.skip("Variáveis SharePoint não configuradas no .env")
        if any(s.startswith("seu_") for s in [settings.SHAREPOINT_CLIENT_ID or "", settings.SHAREPOINT_SITE_URL or ""]):
            pytest.skip("Preencha SHAREPOINT_* no .env com valores reais")
        return True

    def test_sharepoint_auth_get_token(self, env_ok):
        """Verifica se conseguimos obter token do Entra ID."""
        from app.services.sharepoint_auth import SharePointAuthService
        svc = SharePointAuthService()
        token = svc.get_access_token()
        assert token is not None
        assert len(token) > 50

    def test_sharepoint_site_and_drive(self, env_ok):
        """Verifica se conseguimos obter Site ID e Drive ID."""
        from app.services.sharepoint_files import SharePointFileService
        sp = SharePointFileService()
        site_id = sp._get_site_id()
        assert site_id
        drive_id = sp._get_drive_id(site_id)
        assert drive_id

    def test_sharepoint_create_folder_and_upload_and_link(self, env_ok):
        """Cria pasta de teste, faz upload de um arquivo e obtém link de compartilhamento."""
        from app.services.sharepoint_files import SharePointFileService
        sp = SharePointFileService()
        # Pasta de teste: base / ano / "Teste Automatizado" / "99999 - N/A - Teste E2E"
        relative = "2025/Teste Automatizado/99999 - N/A - Teste E2E"
        drive_id, folder_id = sp.ensure_folder_path(relative)
        assert drive_id
        assert folder_id

        # Upload de um arquivo de teste
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Conteudo de teste FluxoNovasFeatures\n")
            tmp_path = Path(f.name)
        try:
            result = sp.upload_file(tmp_path, folder_id=folder_id, drive_id=drive_id, overwrite=True)
            assert result.get("id")
            assert result.get("name")
        finally:
            tmp_path.unlink(missing_ok=True)

        # Link de compartilhamento
        web_url = sp.create_sharing_link(drive_id, folder_id)
        assert web_url
        assert "http" in web_url and "sharepoint" in web_url.lower()
