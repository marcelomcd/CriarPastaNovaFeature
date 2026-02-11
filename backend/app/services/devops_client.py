"""Cliente Azure DevOps REST API: Features, anexos, atualização de campos."""
import base64
import logging
import re
import tempfile
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, unquote

import requests

from app.utils.name_utils import sanitize_attachment_filename
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

    def list_features(
        self,
        include_closed: bool = True,
        updated_since: datetime | None = None,
        only_closed: bool = False,
    ) -> list[WorkItemResponse]:
        """
        Lista Features do projeto (Area Path sob Quali IT ! Gestao de Projetos).
        include_closed: se True, inclui Features encerradas (para varredura).
        updated_since: se informado, retorna apenas Features criadas ou alteradas após essa data (UTC).
        only_closed: se True, retorna apenas Features com estado Encerrado (reduz volume; use com updated_since para só atualizações).
        """
        area = "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos"
        if only_closed:
            state_filter = " AND [System.State] = 'Encerrado'"
        elif include_closed:
            state_filter = ""
        else:
            state_filter = " AND [System.State] <> 'Encerrado'"
        date_filter = ""
        if updated_since is not None:
            # WIQL aceita data em formato ISO; System.ChangedDate é atualizado em criação e em edições (ex.: novo anexo)
            dt = updated_since.strftime("%Y-%m-%dT%H:%M:%SZ")
            date_filter = f" AND [System.ChangedDate] >= '{dt}'"
        wiql = {
            "query": (
                "SELECT [System.Id], [System.Title], [System.AreaPath], [System.CreatedDate], [System.State], "
                "[Custom.NumeroProposta], [Custom.LinkPastaDocumentacao] FROM WorkItems "
                f"WHERE [System.WorkItemType] = 'Feature' AND [System.AreaPath] UNDER '{area}'"
                f"{state_filter}{date_filter} ORDER BY [System.Id] DESC"
            )
        }
        r = self._make_request("POST", "wit/wiql", json=wiql)
        data = r.json()
        work_items = data.get("workItems", [])
        if not work_items:
            return []
        ids = [str(wi["id"]) for wi in work_items]
        return self.get_work_items_by_ids(ids)

    def _wiql_features(self, extra_where: str = "") -> list[WorkItemResponse]:
        """WIQL base para Features (Area Path Gestao de Projetos). extra_where é concatenado com AND."""
        area = "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos"
        where = f"[System.WorkItemType] = 'Feature' AND [System.AreaPath] UNDER '{area}'"
        if extra_where.strip():
            where += " AND " + extra_where.strip()
        wiql = {
            "query": (
                "SELECT [System.Id], [System.Title], [System.AreaPath], [System.CreatedDate], [System.State], "
                "[Custom.NumeroProposta], [Custom.LinkPastaDocumentacao] FROM WorkItems "
                f"WHERE {where} ORDER BY [System.Id] DESC"
            )
        }
        r = self._make_request("POST", "wit/wiql", json=wiql)
        data = r.json()
        work_items = data.get("workItems", [])
        if not work_items:
            return []
        return self.get_work_items_by_ids([str(wi["id"]) for wi in work_items])

    def find_features_by_numero_proposta(self, numero_proposta: str) -> list[WorkItemResponse]:
        """Busca Features pelo Custom.NumeroProposta (ex.: 01234-56). Retorna lista (pode haver mais de uma)."""
        if not (numero_proposta or str(numero_proposta).strip()):
            return []
        prop = str(numero_proposta).strip()
        return self._wiql_features(f"[Custom.NumeroProposta] = '{prop.replace(chr(39), chr(39)+chr(39))}'")

    def find_features_by_title_contains(self, title_fragment: str) -> list[WorkItemResponse]:
        """Busca Features cujo System.Title contém o fragmento. Retorna lista ordenada por ID DESC."""
        if not (title_fragment or str(title_fragment).strip()):
            return []
        frag = str(title_fragment).strip()
        if len(frag) < 2:
            return []
        esc = frag.replace("'", "''")
        return self._wiql_features(f"[System.Title] CONTAINS '{esc}'")

    _AREA_GESTAO = "Quali IT - Inovação e Tecnologia\\Quali IT ! Gestao de Projetos"
    _PROPOSTA_PATTERN = re.compile(r"\d{5}-\d{2}")

    def _is_gestao_feature(self, wi: WorkItemResponse) -> bool:
        """Verifica se o work item é uma Feature da área Gestão de Projetos."""
        fields = wi.fields or {}
        if (fields.get("System.WorkItemType") or "").strip() != "Feature":
            return False
        area = (fields.get("System.AreaPath") or "").strip()
        return area.startswith(self._AREA_GESTAO) or self._AREA_GESTAO in area

    def _client_matches(self, wi: WorkItemResponse, client_name_normalized: str | None) -> bool:
        """True se client_name_normalized for None ou se o último segmento do AreaPath (normalizado) for igual."""
        if not client_name_normalized or not client_name_normalized.strip():
            return True
        from app.utils.name_utils import normalize_client_name

        area = (wi.fields or {}).get("System.AreaPath") or ""
        last = area.split("\\")[-1].strip()
        return normalize_client_name(last).strip().lower() == client_name_normalized.strip().lower()

    def resolve_feature_for_folder_name(
        self, folder_name: str, client_name_normalized: str | None = None
    ) -> WorkItemResponse | None:
        """
        Resolve o nome da pasta para uma Feature no Azure DevOps (ID, Número da Proposta ou Título).
        Ordem: 1) Feature ID (inteiro), 2) Número da Proposta (5d-2d), 3) Título contém.
        Se client_name_normalized for informado, filtra resultados pelo cliente (último segmento do AreaPath).
        """
        name = (folder_name or "").strip()
        if not name:
            return None
        # 1) Tenta como ID
        try:
            wid = int(name)
            wi = self.get_work_item_by_id(wid)
            if wi and self._is_gestao_feature(wi) and self._client_matches(wi, client_name_normalized):
                return wi
        except (ValueError, TypeError):
            pass
        # 2) Tenta como Número da Proposta (ou extrai do nome); DevOps pode armazenar 025288-01 ou 25288-01
        match = self._PROPOSTA_PATTERN.search(name)
        if match:
            prop = match.group(0)
            pre, _, suf = prop.partition("-")
            to_try = [prop]
            if len(pre) == 5:
                to_try.append("0" + prop)  # 25288-01 -> 025288-01
            elif len(pre) == 6 and pre.startswith("0"):
                to_try.append(pre[1:] + "-" + suf)  # 025288-01 -> 25288-01
            for p in to_try:
                for wi in self.find_features_by_numero_proposta(p):
                    if self._client_matches(wi, client_name_normalized):
                        return wi
        # 3) Busca por título contendo o nome da pasta
        for wi in self.find_features_by_title_contains(name):
            if self._client_matches(wi, client_name_normalized):
                return wi
        return None

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
        """
        Atualiza o campo Custom.LinkPastaDocumentacao da Feature.
        Em 400 (ex.: regras de campos obrigatórios como DetalhesForaEscopo/Developer1) não levanta exceção:
        retorna None e registra log; a pasta e os anexos já foram garantidos no SharePoint.
        """
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
        if r.status_code == 400:
            logger.warning(
                "Azure DevOps PATCH work item %s recusado (400). Possível campo obrigatório vazio (ex.: DetalhesForaEscopo, Developer1). Resposta: %s",
                work_item_id,
                (r.text or "")[:500],
            )
            return None
        if r.status_code == 403:
            logger.warning(
                "Azure DevOps PATCH work item %s status 403: %s",
                work_item_id,
                (r.text or "")[:500],
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
        rel == 'AttachedFile'; url termina com /attachments/{id}; attributes.name tem o nome do arquivo.
        """
        result = []
        for rel in work_item.relations or []:
            if rel.get("rel") != "AttachedFile":
                continue
            url = rel.get("url") or ""
            if "/attachments/" not in url:
                continue
            att_id = url.split("/attachments/")[-1].split("?")[0].strip()
            name = (rel.get("attributes") or {}).get("name") or ""
            if not name or name.strip() == "" or name.startswith("attachment_"):
                name = f"attachment_{att_id}"
            result.append((att_id, name.strip()))
        return result

    @staticmethod
    def _filename_from_content_disposition(content_disposition: str | None) -> str | None:
        """Extrai filename do header Content-Disposition (filename=\"...\" ou filename*=UTF-8''...)."""
        if not content_disposition:
            return None
        # filename*=UTF-8''nome%20arquivo.docx
        m = re.search(r"filename\*=UTF-8''([^;\s]+)", content_disposition, re.I)
        if m:
            return unquote(m.group(1).strip())
        # filename="nome.docx"
        m = re.search(r'filename["\']?\s*=\s*["\']?([^"\';\s\n\r]+)', content_disposition, re.I)
        if m:
            return m.group(1).strip()
        return None

    def download_attachment(
        self,
        attachment_id: str,
        file_name: str | None = None,
        destination: Path | None = None,
    ) -> Path:
        """
        Baixa um anexo por ID e retorna o Path do arquivo salvo com o nome original (sanitizado).
        O arquivo é salvo com o mesmo nome/extensão para subir ao SharePoint com nome correto.
        """
        proj = unquote(self.project) if "%" in self.project else self.project
        proj_enc = quote(proj, safe="", encoding="utf-8")
        url = f"{self.base_url}/{proj_enc}/_apis/wit/attachments/{attachment_id}?api-version={self.api_version}"
        r = self.session.get(url, timeout=60)
        r.raise_for_status()
        content = r.content
        # Nome: preferir file_name; senão Content-Disposition; senão attachment_id
        name = (file_name or "").strip()
        if not name or name.startswith("attachment_"):
            name = self._filename_from_content_disposition(r.headers.get("Content-Disposition")) or f"attachment_{attachment_id}"
        safe_name = sanitize_attachment_filename(name)
        if not Path(safe_name).suffix and "." in name:
            ext = Path(name).suffix
            if ext:
                safe_name = safe_name.rstrip(".") + ext
        if destination is None:
            temp_dir = Path(tempfile.mkdtemp())
            destination = temp_dir / safe_name
            # Evitar sobrescrever se houver dois anexos com mesmo nome
            base = destination.stem
            suffix = destination.suffix
            n = 1
            while destination.exists():
                destination = temp_dir / f"{base}_{n}{suffix}"
                n += 1
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        return destination

    def close(self) -> None:
        self.session.close()
