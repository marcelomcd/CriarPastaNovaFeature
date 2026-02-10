"""Cliente Azure DevOps REST API: Features, anexos, atualização de campos."""
import base64
import logging
from pathlib import Path
from urllib.parse import quote, unquote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.config import settings
from app.models.devops_models import WorkItemResponse, LINK_PASTA_DOCUMENTACAO_FIELD

logger = logging.getLogger(__name__)


class AzureDevOpsClient:
    """Cliente para Azure DevOps: listar Features, obter anexos, atualizar Custom.LinkPastaDocumentacao."""

    def __init__(self, pat: str | None = None) -> None:
        self.pat = (pat or settings.AZURE_DEVOPS_PAT or "").strip()
        self.org = settings.AZURE_DEVOPS_ORG
        self.project = settings.AZURE_DEVOPS_PROJECT
        self.api_version = "7.1"
        if self.org.startswith("$(") and self.org.endswith(")"):
            self.org = "qualiit"
        self.base_url = f"https://dev.azure.com/{self.org}"
        if not self.pat or self.pat == "SEU_PAT_AQUI":
            raise ValueError("AZURE_DEVOPS_PAT não está configurado")
        self.session = requests.Session()
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(pool_connections=10, pool_maxsize=20, max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update({
            "Authorization": f"Basic {self._encode_pat()}",
            "Content-Type": "application/json",
        })

    def _encode_pat(self) -> str:
        return base64.b64encode(f":{self.pat}".encode("utf-8")).decode("utf-8")

    def _project_url(self, endpoint: str, *, params: dict | None = None) -> tuple[str, dict]:
        proj = unquote(self.project) if "%" in self.project else self.project
        proj_enc = quote(proj, safe="", encoding="utf-8")
        url = f"{self.base_url}/{proj_enc}/_apis/{endpoint}"
        p = params or {}
        p.setdefault("api-version", self.api_version)
        return url, p

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        params = kwargs.pop("params", {})
        url, merged = self._project_url(endpoint, params=params)
        kwargs["params"] = {**merged, **params}
        r = self.session.request(method=method, url=url, timeout=30, **kwargs)
        if r.status_code in (401, 403) or "/_signin" in (r.url or ""):
            raise ValueError("Erro de autenticação. Verifique AZURE_DEVOPS_PAT.")
        if "text/html" in (r.headers.get("Content-Type") or "") and r.status_code != 200:
            raise ValueError(f"Resposta inesperada (HTML). Status: {r.status_code}")
        r.raise_for_status()
        return r

    def list_features(self, include_closed: bool = True) -> list[WorkItemResponse]:
        """
        Lista Features do projeto (Area Path sob Quali IT ! Gestao de Projetos).
        include_closed: se True, inclui Features encerradas (para varredura).
        """
        area = "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos"
        state_filter = "" if include_closed else " AND [System.State] <> 'Encerrado'"
        wiql = {
            "query": (
                "SELECT [System.Id], [System.Title], [System.AreaPath], [System.CreatedDate], [System.State], "
                "[Custom.NumeroProposta], [Custom.LinkPastaDocumentacao] FROM WorkItems "
                f"WHERE [System.WorkItemType] = 'Feature' AND [System.AreaPath] UNDER '{area}'"
                f"{state_filter} ORDER BY [System.Id] DESC"
            )
        }
        r = self._make_request("POST", "wit/wiql", json=wiql)
        data = r.json()
        work_items = data.get("workItems", [])
        if not work_items:
            return []
        ids = [str(wi["id"]) for wi in work_items]
        return self.get_work_items_by_ids(ids)

    def get_work_items_by_ids(self, ids: list[str]) -> list[WorkItemResponse]:
        """Obtém Work Items por IDs (com $expand=all para relations/anexos). Faz batch de 200 por request (limite da API)."""
        if not ids:
            return []
        out = []
        batch_size = 200
        for i in range(0, len(ids), batch_size):
            batch = ids[i : i + batch_size]
            r = self._make_request("GET", "wit/workitems", params={"ids": ",".join(batch), "$expand": "all"})
            data = r.json()
            for item in data.get("value", []):
                out.append(WorkItemResponse(
                    id=item["id"],
                    rev=item["rev"],
                    fields=item.get("fields", {}),
                    relations=item.get("relations"),
                    url=item.get("url", ""),
                ))
        return out

    def get_work_item_by_id(self, work_item_id: int) -> WorkItemResponse | None:
        """Obtém um Work Item por ID (com relations para anexos)."""
        try:
            r = self._make_request("GET", f"wit/workitems/{work_item_id}", params={"$expand": "all"})
            item = r.json()
            return WorkItemResponse(
                id=item["id"],
                rev=item["rev"],
                fields=item.get("fields", {}),
                relations=item.get("relations"),
                url=item.get("url", ""),
            )
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                return None
            raise
        except ValueError:
            raise

    def update_work_item_link_pasta(self, work_item_id: int, link_url: str) -> WorkItemResponse | None:
        """Atualiza o campo Custom.LinkPastaDocumentacao da Feature."""
        body = [{"op": "replace", "path": f"/fields/{LINK_PASTA_DOCUMENTACAO_FIELD}", "value": link_url}]
        proj = unquote(self.project) if "%" in self.project else self.project
        proj_enc = quote(proj, safe="", encoding="utf-8")
        url = f"{self.base_url}/{proj_enc}/_apis/wit/workitems/{work_item_id}?api-version={self.api_version}"
        r = self.session.patch(
            url,
            json=body,
            headers={"Content-Type": "application/json-patch+json"},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        return WorkItemResponse(
            id=data["id"],
            rev=data["rev"],
            fields=data.get("fields", {}),
            relations=data.get("relations"),
            url=data.get("url", ""),
        )

    def list_attachment_relations(self, work_item: WorkItemResponse) -> list[tuple[str, str]]:
        """
        Extrai (attachment_id, name) dos relations do work item.
        rel == 'AttachedFile'; url termina com /attachments/{id}; attributes.name pode ter o nome do arquivo.
        """
        result = []
        for rel in work_item.relations or []:
            if rel.get("rel") != "AttachedFile":
                continue
            url = rel.get("url") or ""
            if "/attachments/" not in url:
                continue
            att_id = url.split("/attachments/")[-1].split("?")[0].strip()
            name = (rel.get("attributes") or {}).get("name") or f"attachment_{att_id}"
            result.append((att_id, name))
        return result

    def download_attachment(
        self,
        attachment_id: str,
        file_name: str | None = None,
        destination: Path | None = None,
    ) -> Path:
        """Baixa um anexo por ID e retorna o Path do arquivo salvo."""
        proj = unquote(self.project) if "%" in self.project else self.project
        proj_enc = quote(proj, safe="", encoding="utf-8")
        url = f"{self.base_url}/{proj_enc}/_apis/wit/attachments/{attachment_id}?api-version={self.api_version}"
        r = self.session.get(url, timeout=60)
        r.raise_for_status()
        content = r.content
        if destination is None:
            import tempfile
            suffix = Path(file_name or "attachment").suffix or ".bin"
            f = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            destination = Path(f.name)
            f.close()
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        return destination

    def close(self) -> None:
        self.session.close()
