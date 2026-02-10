"""Serviço para criar pastas, links de compartilhamento e upload no SharePoint (Microsoft Graph)."""
import logging
from pathlib import Path
from urllib.parse import quote

import requests

from app.config import settings
from app.services.sharepoint_auth import SharePointAuthService

logger = logging.getLogger(__name__)


class SharePointFileService:
    """Gerencia pastas e arquivos no SharePoint via Microsoft Graph."""

    def __init__(
        self,
        site_url: str | None = None,
        folder_path_base: str | None = None,
        auth_service: SharePointAuthService | None = None,
    ) -> None:
        self.site_url = (site_url or settings.SHAREPOINT_SITE_URL or "").rstrip("/")
        self.folder_path_base = folder_path_base or settings.SHAREPOINT_FOLDER_PATH_BASE
        if not self.site_url:
            raise ValueError("SHAREPOINT_SITE_URL não está configurado")
        self.auth_service = auth_service or SharePointAuthService()
        self.graph_base_url = "https://graph.microsoft.com/v1.0"
        self._parse_site_info()

    def _parse_site_info(self) -> None:
        """Extrai hostname e nome do site da URL."""
        from urllib.parse import urlparse

        parsed = urlparse(self.site_url)
        self.hostname = parsed.netloc
        path_parts = [p for p in parsed.path.split("/") if p]
        if "sites" in path_parts:
            idx = path_parts.index("sites")
            self.site_name = path_parts[idx + 1] if idx + 1 < len(path_parts) else ""
        else:
            self.site_name = path_parts[-1] if path_parts else ""

    def _get_site_id(self) -> str:
        """Obtém o Site ID do SharePoint."""
        token = self.auth_service.get_access_token()
        url = (
            f"{self.graph_base_url}/sites/{self.hostname}:/sites/{self.site_name}"
            if self.site_name
            else f"{self.graph_base_url}/sites/{self.hostname}"
        )
        r = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            timeout=30,
        )
        r.raise_for_status()
        site_id = r.json().get("id")
        if not site_id:
            raise ValueError("Site ID não encontrado na resposta")
        return site_id

    def _get_drive_id(self, site_id: str, drive_name_preference: str | None = None) -> str:
        """Obtém o Drive ID (biblioteca de documentos)."""
        token = self.auth_service.get_access_token()
        r = requests.get(
            f"{self.graph_base_url}/sites/{site_id}/drives",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            timeout=30,
        )
        r.raise_for_status()
        drives = r.json().get("value", [])
        if not drives:
            raise ValueError("Nenhum drive encontrado no site")
        preferred = []
        if drive_name_preference:
            preferred.append(drive_name_preference)
        preferred.extend(["Documentações de Projetos", "Documentos Compartilhados", "Shared Documents"])
        for name in preferred:
            for d in drives:
                if name.lower() in (d.get("name") or "").lower():
                    did = d.get("id")
                    if did:
                        return did
        return drives[0]["id"]

    def _get_folder_id(self, drive_id: str, folder_path: str) -> str | None:
        """Obtém o ID de uma pasta pelo caminho. Retorna None se não existir."""
        if not folder_path or folder_path.strip() == "":
            return "root"
        token = self.auth_service.get_access_token()
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        path_parts = folder_path.split("/")
        encoded = "/".join(quote(p, safe="") for p in path_parts)
        url = f"{self.graph_base_url}/drives/{drive_id}/root:/{encoded}"
        try:
            r = requests.get(url, headers=headers, timeout=30)
            if r.status_code == 200:
                return r.json().get("id")
            if r.status_code == 404:
                return None
            r.raise_for_status()
        except requests.RequestException:
            return None
        return None

    def get_folder_id_by_relative_path(self, drive_id: str, relative_path: str) -> str | None:
        """Obtém o ID da pasta pelo caminho relativo à base. Retorna None se não existir."""
        full = f"{self.folder_path_base}/{relative_path}".strip("/").replace("//", "/")
        return self._get_folder_id(drive_id, full)

    def list_folder_children(self, drive_id: str, folder_id: str) -> list[dict]:
        """Lista itens (arquivos e subpastas) diretos da pasta. Cada item tem id, name, file ou folder."""
        token = self.auth_service.get_access_token()
        url = f"{self.graph_base_url}/drives/{drive_id}/items/{folder_id}/children"
        r = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            timeout=30,
        )
        r.raise_for_status()
        return r.json().get("value", [])

    def download_item_content(self, drive_id: str, item_id: str) -> bytes:
        """Baixa o conteúdo de um item (arquivo)."""
        token = self.auth_service.get_access_token()
        url = f"{self.graph_base_url}/drives/{drive_id}/items/{item_id}/content"
        r = requests.get(
            url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=60,
        )
        r.raise_for_status()
        return r.content

    def delete_item(self, drive_id: str, item_id: str) -> None:
        """Remove um item (arquivo ou pasta e conteúdo)."""
        token = self.auth_service.get_access_token()
        url = f"{self.graph_base_url}/drives/{drive_id}/items/{item_id}"
        r = requests.delete(url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
        r.raise_for_status()

    def copy_folder_contents_to(
        self,
        drive_id: str,
        source_folder_id: str,
        target_folder_id: str,
    ) -> None:
        """
        Copia todos os arquivos (apenas um nível) da pasta source para a pasta target.
        Usado para mover Feature encerrada de Ano/Cliente/Feature para Ano/Closed/Cliente/Feature.
        """
        children = self.list_folder_children(drive_id, source_folder_id)
        for item in children:
            if item.get("file") is not None:
                name = item.get("name") or ""
                item_id = item.get("id")
                if not name or not item_id:
                    continue
                content = self.download_item_content(drive_id, item_id)
                tmp = Path(Path(name).name)
                try:
                    tmp.write_bytes(content)
                    self.upload_file(tmp, target_folder_id, drive_id=drive_id, overwrite=True, upload_name=name)
                finally:
                    try:
                        tmp.unlink(missing_ok=True)
                    except OSError:
                        pass
            # Subpastas não copiadas (estrutura é plana: Feature só tem arquivos)
        self.delete_item(drive_id, source_folder_id)

    def _create_folder(self, drive_id: str, parent_id: str, name: str) -> str:
        """Cria uma pasta dentro de parent_id e retorna o item id."""
        token = self.auth_service.get_access_token()
        url = f"{self.graph_base_url}/drives/{drive_id}/items/{parent_id}/children"
        body = {"name": name, "folder": {}, "@microsoft.graph.conflictBehavior": "fail"}
        r = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=30,
        )
        if r.status_code == 409:
            # Pasta já existe; listar children e achar pelo nome
            list_url = f"{self.graph_base_url}/drives/{drive_id}/items/{parent_id}/children"
            rr = requests.get(
                list_url,
                headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
                timeout=30,
            )
            rr.raise_for_status()
            for item in rr.json().get("value", []):
                if item.get("name") == name and item.get("folder"):
                    return item["id"]
            raise ValueError(f"Conflito ao criar pasta '{name}' e não encontrada na listagem")
        r.raise_for_status()
        return r.json()["id"]

    def ensure_folder_path(self, relative_path: str) -> tuple[str, str]:
        """
        Garante que a pasta (e subpastas) existem. Cria em cadeia se necessário.
        relative_path: ex. "2025/Camil Alimentos/12345 - N/A - Título"
        Retorna (drive_id, folder_item_id).
        """
        full_path = f"{self.folder_path_base}/{relative_path}".strip("/").replace("//", "/")
        site_id = self._get_site_id()
        drive_id = self._get_drive_id(site_id)
        existing = self._get_folder_id(drive_id, full_path)
        if existing:
            return (drive_id, existing)
        base_id = self._get_folder_id(drive_id, self.folder_path_base)
        if not base_id:
            base_id = "root"
            base_parts = self.folder_path_base.split("/")
            for part in base_parts:
                if not part.strip():
                    continue
                base_id = self._create_folder(drive_id, base_id, part)
        rel_parts = [p for p in relative_path.split("/") if p.strip()]
        parent_id = base_id
        for part in rel_parts:
            token = self.auth_service.get_access_token()
            list_url = f"{self.graph_base_url}/drives/{drive_id}/items/{parent_id}/children"
            r = requests.get(
                list_url,
                headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
                timeout=30,
            )
            r.raise_for_status()
            found = None
            for item in r.json().get("value", []):
                if item.get("name") == part and item.get("folder"):
                    found = item["id"]
                    break
            parent_id = found or self._create_folder(drive_id, parent_id, part)
        return (drive_id, parent_id)

    def create_sharing_link(self, drive_id: str, item_id: str) -> str:
        """
        Cria (ou retorna existente) link de compartilhamento para a pasta.
        Retorna a URL do link (webUrl).
        """
        token = self.auth_service.get_access_token()
        url = f"{self.graph_base_url}/drives/{drive_id}/items/{item_id}/createLink"
        body = {"type": "view", "scope": "organization"}
        r = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        link = data.get("link")
        if isinstance(link, dict) and link.get("webUrl"):
            return link["webUrl"]
        return data.get("webUrl", "")

    def upload_file(
        self,
        file_path: Path,
        folder_id: str,
        drive_id: str | None = None,
        overwrite: bool = True,
        upload_name: str | None = None,
    ) -> dict:
        """Faz upload de um arquivo para a pasta indicada por folder_id. upload_name define o nome no SharePoint (default: file_path.name)."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(str(file_path))
        if drive_id is None:
            site_id = self._get_site_id()
            drive_id = self._get_drive_id(site_id)
        token = self.auth_service.get_access_token()
        content = file_path.read_bytes()
        name = (upload_name or file_path.name).strip() or file_path.name
        encoded_name = quote(name, safe="")
        url = f"{self.graph_base_url}/drives/{drive_id}/items/{folder_id}:/{encoded_name}:/content"
        if overwrite:
            url += "?@microsoft.graph.conflictBehavior=replace"
        if len(content) > 4 * 1024 * 1024:
            return self._upload_large_file(drive_id, folder_id, name, content, token)
        r = requests.put(
            url,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/octet-stream"},
            data=content,
            timeout=300,
        )
        r.raise_for_status()
        d = r.json()
        return {"id": d.get("id"), "name": d.get("name"), "web_url": d.get("webUrl")}

    def _upload_large_file(
        self,
        drive_id: str,
        folder_id: str,
        name_or_path: str | Path,
        content: bytes,
        access_token: str,
    ) -> dict:
        """Upload session para arquivos > 4MB. name_or_path: nome do arquivo (str) ou Path."""
        name = name_or_path.name if isinstance(name_or_path, Path) else str(name_or_path)
        session_url = f"{self.graph_base_url}/drives/{drive_id}/items/{folder_id}:/{quote(name, safe='')}:/createUploadSession"
        r = requests.post(
            session_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json={"item": {"@microsoft.graph.conflictBehavior": "replace", "name": name}},
            timeout=30,
        )
        r.raise_for_status()
        upload_url = r.json().get("uploadUrl")
        if not upload_url:
            raise ValueError("createUploadSession não retornou uploadUrl")
        chunk_size = 4 * 1024 * 1024
        total = len(content)
        for start in range(0, total, chunk_size):
            end = min(start + chunk_size, total)
            chunk = content[start:end]
            rr = requests.put(
                upload_url,
                headers={
                    "Content-Length": str(len(chunk)),
                    "Content-Range": f"bytes {start}-{end - 1}/{total}",
                },
                data=chunk,
                timeout=300,
            )
            if rr.status_code in (200, 201):
                d = rr.json()
                return {"id": d.get("id"), "name": d.get("name"), "web_url": d.get("webUrl")}
            if rr.status_code != 202:
                rr.raise_for_status()
        raise ValueError("Upload em chunks não retornou item final")
