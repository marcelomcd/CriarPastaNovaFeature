"""
Testes de integração: leitura no Azure DevOps (Features, work item).
Requer .env com AZURE_DEVOPS_PAT e projeto configurado. Execute com: pytest -m integration
Não alteramos dados no DevOps (apenas leitura) para evitar efeitos colaterais.
"""
import pytest

pytest.importorskip("app")


@pytest.mark.integration
class TestAzureDevOpsIntegration:
    """Testes de integração com Azure DevOps (somente leitura)."""

    @pytest.fixture(scope="class")
    def env_ok(self):
        """Só roda se PAT e projeto estiverem configurados (via .env)."""
        from app.config import settings
        pat = (settings.AZURE_DEVOPS_PAT or "").strip()
        if not pat or "seu_" in pat.lower() or pat == "SEU_PAT_AQUI":
            pytest.skip("AZURE_DEVOPS_PAT não configurado no .env")
        return True

    def test_devops_list_features(self, env_ok):
        """Lista Features (leitura) e verifica estrutura."""
        from app.services.devops_client import AzureDevOpsClient
        client = AzureDevOpsClient()
        features = client.list_features(include_closed=True)
        # Pode ser 0 ou mais
        assert isinstance(features, list)
        for wi in features[:3]:  # só primeiros 3
            assert hasattr(wi, "id")
            assert hasattr(wi, "fields")
            assert "System.Title" in wi.fields or "System.WorkItemType" in wi.fields

    def test_devops_get_work_item_if_exists(self, env_ok):
        """Obtém um work item por ID (usa o primeiro da lista se houver)."""
        from app.services.devops_client import AzureDevOpsClient
        client = AzureDevOpsClient()
        features = client.list_features(include_closed=True)
        if not features:
            pytest.skip("Nenhuma Feature no projeto para testar get")
        first_id = features[0].id
        wi = client.get_work_item_by_id(first_id)
        assert wi is not None
        assert wi.id == first_id
        assert wi.fields

    def test_devops_list_attachment_relations(self, env_ok):
        """Verifica se list_attachment_relations extrai IDs (pode ser vazio)."""
        from app.services.devops_client import AzureDevOpsClient
        from app.models.devops_models import WorkItemResponse
        client = AzureDevOpsClient()
        features = client.list_features(include_closed=True)
        if not features:
            pytest.skip("Nenhuma Feature para testar anexos")
        # Pega uma Feature que tenha relations
        for wi in features[:5]:
            rels = client.list_attachment_relations(wi)
            assert isinstance(rels, list)
            for item in rels:
                assert len(item) == 2  # (id, name)
            break
