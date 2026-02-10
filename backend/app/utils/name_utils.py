"""Utilitários para normalização de nomes (cliente, título de pasta)."""
import re
from typing import Optional

# Caracteres inválidos em nomes de pasta (Windows/SharePoint)
INVALID_FOLDER_CHARS = re.compile(r'[\\/:*?"<>|]')

# Para nomes de arquivo (anexos): remove caracteres perigosos para filesystem
INVALID_FILE_CHARS = re.compile(r'[\\/:*?"<>|\x00]')

# Tamanho máximo típico para nome de pasta (SharePoint/OneDrive)
MAX_FOLDER_NAME_LENGTH = 255


def normalize_client_name(area_path_last_segment: str) -> str:
    """
    Normaliza o nome do cliente para exibição e uso em pasta.

    Regra: title case por palavra. Ex.: "CAMIL ALIMENTOS" -> "Camil Alimentos".
    Remove caracteres inválidos para pasta.

    Args:
        area_path_last_segment: Último segmento do Area Path (após a última barra invertida).

    Returns:
        Nome normalizado (title case, sem caracteres inválidos).
    """
    if not area_path_last_segment or not area_path_last_segment.strip():
        return "Sem Cliente"
    s = area_path_last_segment.strip()
    # Remove caracteres inválidos
    s = INVALID_FOLDER_CHARS.sub(" ", s)
    # Title case por palavra (primeira letra maiúscula, resto minúscula)
    s = " ".join(word.capitalize() for word in s.split())
    return s.strip() or "Sem Cliente"


def sanitize_folder_name(title: str, max_length: Optional[int] = None) -> str:
    """
    Sanitiza um título para uso como nome de pasta.

    Remove ou substitui caracteres inválidos \\ / : * ? " < > |
    e limita o tamanho se necessário.

    Args:
        title: Título original (ex.: System.Title da Feature).
        max_length: Tamanho máximo (default MAX_FOLDER_NAME_LENGTH).

    Returns:
        String segura para nome de pasta.
    """
    if not title:
        return ""
    max_len = max_length or MAX_FOLDER_NAME_LENGTH
    s = INVALID_FOLDER_CHARS.sub(" ", str(title).strip())
    # Colapsa múltiplos espaços
    s = " ".join(s.split())
    if len(s) > max_len:
        s = s[: max_len - 3].rstrip() + "..."
    return s.strip()


def sanitize_attachment_filename(name: str, max_length: int = 200) -> str:
    """
    Sanitiza o nome de um anexo para uso como nome de arquivo no disco/SharePoint.
    Remove path e caracteres inválidos; preserva a extensão.
    """
    if not name or not str(name).strip():
        return "attachment"
    s = str(name).strip()
    # Remove path (só o nome do arquivo)
    s = s.split("\\")[-1].split("/")[-1]
    s = INVALID_FILE_CHARS.sub("_", s)
    s = " ".join(s.split())
    if len(s) > max_length:
        ext = ""
        if "." in s:
            s, ext = s.rsplit(".", 1)
            ext = "." + ext
        s = s[: max_length - len(ext) - 1].rstrip("._") + ext
    return s.strip() or "attachment"


def build_feature_folder_name(
    feature_id: int,
    numero_proposta: Optional[str],
    title: str,
    proposta_placeholder: str = "N/A",
) -> str:
    """
    Monta o nome da pasta da Feature: "{FeatureId} - {NumeroProposta} - {Titulo}".

    Args:
        feature_id: System.Id da Feature.
        numero_proposta: Custom.NumeroProposta (pode ser vazio).
        title: System.Title (será sanitizado).
        proposta_placeholder: Texto quando numero_proposta estiver vazio.

    Returns:
        Nome da pasta (ex.: "12345 - N/A - Implementar login").
    """
    prop = (numero_proposta or "").strip() or proposta_placeholder
    tit = sanitize_folder_name(title, max_length=200) or "Sem título"
    return f"{feature_id} - {prop} - {tit}"
