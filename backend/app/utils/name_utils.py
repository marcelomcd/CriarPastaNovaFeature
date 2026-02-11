"""Utilitários para normalização de nomes (cliente, título de pasta)."""
import re
from typing import Optional

# Caracteres inválidos em nomes de pasta (Windows/SharePoint)
INVALID_FOLDER_CHARS = re.compile(r'[\\/:*?"<>|]')

# Para nomes de arquivo (anexos): remove caracteres perigosos para filesystem
INVALID_FILE_CHARS = re.compile(r'[\\/:*?"<>|\x00]')

# Tamanho máximo típico para nome de pasta (SharePoint/OneDrive)
MAX_FOLDER_NAME_LENGTH = 255

# Nomes reservados Windows/SharePoint (case-insensitive) – não podem ser usados como nome de pasta
RESERVED_FOLDER_NAMES = frozenset(
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{i}" for i in range(1, 10)}
    | {f"LPT{i}" for i in range(1, 10)}
)


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


def sanitize_folder_name_for_sharepoint(segment: str) -> str:
    """
    Ajusta um segmento de caminho para criação de pasta no SharePoint/Graph API.
    Remove pontos e espaços no final (rejeitados pela API), evita nomes reservados (CON, NUL, etc.).
    """
    if not segment or not str(segment).strip():
        return "Unnamed"
    s = str(segment).strip().rstrip(". ")
    if not s:
        return "Unnamed"
    if s.upper() in RESERVED_FOLDER_NAMES:
        return f"{s}_"
    return s


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


# Padrão Número da Proposta: 5 dígitos, hífen, 2 dígitos (ex.: 01234-56)
NUMERO_PROPOSTA_PATTERN = re.compile(r"\d{5}-\d{2}", re.IGNORECASE)


def _title_without_duplicate_proposta(title: str, numero_proposta: Optional[str]) -> str:
    """
    Remove do título a primeira ocorrência do número da proposta, se for igual,
    para evitar duplicar no nome da pasta (ex.: "12345 - 01234-56 - 01234-56 Algo" -> "12345 - 01234-56 - Algo").
    """
    if not title or not numero_proposta:
        return title or ""
    prop = (numero_proposta or "").strip()
    if not prop or prop == "N/A":
        return title
    # Se o título começa com o mesmo número da proposta (ex.: "01234-56 Descrição"), remove
    tit = title.strip()
    if tit.startswith(prop):
        rest = tit[len(prop) :].strip().lstrip(" -:")
        return rest or tit
    # Remove ocorrência do padrão 5d-2d se for igual ao numero_proposta em qualquer posição
    match = NUMERO_PROPOSTA_PATTERN.search(tit)
    if match and match.group(0) == prop:
        # Remove essa ocorrência e colapsa espaços
        before = tit[: match.start()].strip().rstrip(" -")
        after = tit[match.end() :].strip().lstrip(" -")
        parts = [p for p in (before, after) if p]
        return " ".join(parts) if parts else tit
    return tit


def build_feature_folder_name(
    feature_id: int,
    numero_proposta: Optional[str],
    title: str,
    proposta_placeholder: str = "N/A",
) -> str:
    """
    Monta o nome da pasta da Feature: "{FeatureId} - {NumeroProposta} - {Titulo}".
    Se o título já contiver o número da proposta (ex.: 01234-56), evita duplicar no nome.

    Args:
        feature_id: System.Id da Feature.
        numero_proposta: Custom.NumeroProposta (pode ser vazio).
        title: System.Title (será sanitizado; duplicata de numero_proposta é removida).
        proposta_placeholder: Texto quando numero_proposta estiver vazio.

    Returns:
        Nome da pasta (ex.: "12345 - 01234-56 - Implementar login").
    """
    prop = (numero_proposta or "").strip() or proposta_placeholder
    tit_raw = _title_without_duplicate_proposta(title or "", numero_proposta if prop != "N/A" else None)
    tit = sanitize_folder_name(tit_raw, max_length=200) or "Sem título"
    return f"{feature_id} - {prop} - {tit}"


# Padrão da pasta de Feature: "ID - Nº Proposta ou N/A - Título"
FEATURE_FOLDER_NAME_PATTERN = re.compile(
    r"^\d+\s*-\s*(\d{5}-\d{2}|N/A)\s*-\s*.+",
    re.IGNORECASE,
)


def is_canonical_feature_folder_name(folder_name: str) -> bool:
    """
    Verifica se o nome da pasta segue o padrão: "Feature ID - Número Proposta - Título"
    (ex.: 12345 - 01234-56 - Título ou 12345 - N/A - Título).
    """
    return bool(folder_name and FEATURE_FOLDER_NAME_PATTERN.match((folder_name or "").strip()))
