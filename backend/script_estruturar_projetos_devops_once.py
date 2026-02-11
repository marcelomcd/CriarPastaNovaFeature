"""
Script de execução ÚNICA para reorganizar a pasta Projetos DevOps no SharePoint.

Objetivo: colocar pastas de empresas (Arteb, Aryzta, etc.) que estão na raiz de
Projetos DevOps dentro da estrutura Ano > Cliente > Feature.

- Lista a raiz de Projetos DevOps.
- Pastas que são anos (2020, 2021, ... 2026) são ignoradas na primeira passagem.
- Para cada pasta que NÃO é ano na raiz (ex.: Arteb, Aryzta): lista subpastas; para cada
  subpasta, busca a Feature no Azure DevOps (por ID, Número da Proposta ou Título)
  para obter o ano e o cliente; move para Ano/Cliente/Feature ID - Nº Proposta - Título.
- Em seguida: para cada pasta de ano (2020-2023, 2024, 2025, 2026), percorre o conteúdo.
  Pastas com nome de Feature (ex.: 25288-01 - Belliz- ...) ou subpastas dentro de pasta de cliente
  são consultadas no Azure DevOps (Feature ID, Nº Proposta ou Título) para obter ano de criação
  e cliente; são então movidas para o caminho correto: Projetos DevOps > Ano > Cliente > Feature ID - Nº Proposta - Título.
- Se não for possível obter a Feature no Azure DevOps, mantém em 2020-2023/Cliente ou 2020-2023/Unknown.
- Ao final: em cada ano, se existirem "Qualiit" e "Quali It", move o conteúdo de Qualiit para Quali It.
- Varredura final em 2020-2023: para cada pasta ali (ex.: 25539-01 - BELLIZ - VALIDACAO...), resolve a Feature
  no Azure DevOps; se a pasta canônica (Feature ID - Nº Proposta - Título) já existir no ano/cliente correto
  (ex.: 2025/Belliz/14796 - 025539-01 - ...), remove a pasta duplicada em 2020-2023.

Execute UMA VEZ manualmente. Não faz parte da pipeline (segunda 5h).
Requer: backend\\.env com AZURE_DEVOPS_PAT, SharePoint configurado.
"""
import logging
import re
import sys
from pathlib import Path

_backend = Path(__file__).resolve().parent
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

from app.config import settings
from app.services.devops_client import AzureDevOpsClient
from app.services.feature_folder_service import work_item_to_feature_info, feature_info_to_folder_path
from app.services.sharepoint_files import SharePointFileService
from app.utils.name_utils import normalize_client_name, sanitize_folder_name_for_sharepoint

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Pastas na raiz que são anos (4 dígitos) ou o container para Features sem ano conhecido
YEAR_PATTERN = re.compile(r"^(202[0-9]|201[0-9])$")  # 2010-2029
FALLBACK_YEAR_FOLDER = "2020-2023"

# Mesma empresa: conteúdo de QUALIIT_SOURCE deve ser movido para QUALI_IT_TARGET (por ano)
QUALIIT_SOURCE_NAME = "Qualiit"  # nome exato ou case-insensitive
QUALI_IT_TARGET_NAME = "Quali It"


def _same_client_qualiit(name: str) -> str | None:
    """Retorna 'source' se for Qualiit, 'target' se for Quali It (mesma empresa), senão None."""
    n = (name or "").strip()
    if not n:
        return None
    low = " ".join(n.lower().split())  # normaliza espaços
    if low == "qualiit":
        return "source"
    if low == "quali it":
        return "target"
    return None


def _is_year_folder(name: str) -> bool:
    """True se o nome for uma pasta de ano (ex.: 2024, 2025) ou 2020-2023."""
    n = (name or "").strip()
    return bool(YEAR_PATTERN.match(n) or n == FALLBACK_YEAR_FOLDER)


# Número da Proposta: 5 dígitos-hífen-2 dígitos (ex.: 25288-01, 025288-01)
PROPOSTA_PATTERN = re.compile(r"\d{5}-\d{2}")


def _looks_like_feature_folder(name: str) -> bool:
    """True se o nome parecer uma pasta de Feature (contém Nº proposta ou 'ID - ...')."""
    n = (name or "").strip()
    if not n or len(n) < 5:
        return False
    if PROPOSTA_PATTERN.search(n):
        return True
    # Formato "número - algo - algo" (ex.: 25288-01 - Belliz - ...)
    if re.match(r"^\d+[\s-]", n):
        return True
    return False


def _process_folder_and_move(
    sp: SharePointFileService,
    devops: AzureDevOpsClient,
    drive_id: str,
    folder_id: str,
    folder_name: str,
    current_year_folder: str,
    client_hint: str | None,
) -> tuple[bool, str | None]:
    """
    Resolve a pasta no Azure DevOps (Feature ID, Nº Proposta ou Título), obtém ano e cliente,
    e move para Projetos DevOps > Ano > Cliente > Feature ID - Nº Proposta - Título.
    Se já existir pasta com o nome canônico no destino, ignora o movimento (evita 409 Conflict).
    Retorna (moveu, mensagem_erro).
    """
    try:
        wi = devops.resolve_feature_for_folder_name(folder_name, client_hint)
        if not wi:
            return (False, None)
        info = work_item_to_feature_info(wi)
        path = feature_info_to_folder_path(info)
        rel = path.relative_path()
        target_parent_rel = "/".join(rel.split("/")[:-1])
        canonical_name = path.folder_name
        parent_rel_sanitized = "/".join(
            sanitize_folder_name_for_sharepoint(p) for p in target_parent_rel.split("/") if p.strip()
        )
        _d, dest_parent_id = sp.ensure_folder_path(parent_rel_sanitized)
        name_para_sharepoint = sanitize_folder_name_for_sharepoint(canonical_name)

        # Evita 409: se já existe pasta com o nome canônico no destino, não move
        existing = sp.list_folder_children(drive_id, dest_parent_id)
        name_lower = (name_para_sharepoint or "").strip().lower()
        for child in existing:
            if child.get("folder") and (child.get("name") or "").strip().lower() == name_lower:
                logger.info(
                    "  [%s] Pasta já existe no destino %s/%s, ignorando: %s",
                    current_year_folder, target_parent_rel, canonical_name, folder_name,
                )
                return (False, None)

        sp.move_item(drive_id, folder_id, dest_parent_id, new_name=name_para_sharepoint)
        logger.info("  [%s] Movido: %s -> %s/%s", current_year_folder, folder_name, target_parent_rel, canonical_name)
        return (True, None)
    except Exception as e:
        err_msg = str(e)
        # 409 Conflict = já existe item com esse nome no destino; tratar como "ignorar" em vez de erro
        if "409" in err_msg or "Conflict" in err_msg:
            logger.info(
                "  [%s] Destino já contém pasta com nome canônico, ignorando movimento: %s",
                current_year_folder, folder_name,
            )
            return (False, None)
        return (False, err_msg)


def _reorganize_year_folder_contents(
    sp: SharePointFileService,
    devops: AzureDevOpsClient,
    drive_id: str,
    base_id: str,
) -> tuple[int, int]:
    """
    Percorre cada pasta de ano (2020-2023, 2024, 2025, 2026). Para cada item dentro do ano:
    - Se for pasta com nome de Feature (Nº proposta ou ID - ...): resolve no Azure DevOps e move
      para Ano > Cliente > Feature ID - Nº Proposta - Título.
    - Se for pasta que parece cliente (ex.: Arteb, Aurora): lista subpastas e processa cada uma
      da mesma forma.
    Retorna (movidos, erros).
    """
    moved = 0
    errors = 0
    children = sp.list_folder_children(drive_id, base_id)
    year_folders = [((c.get("name") or "").strip(), c["id"]) for c in children if c.get("folder") and _is_year_folder((c.get("name") or "").strip())]
    for year_name, year_id in year_folders:
        sub = sp.list_folder_children(drive_id, year_id)
        for item in sub:
            if not item.get("folder"):
                continue
            name = (item.get("name") or "").strip()
            item_id = item.get("id")
            if not name or not item_id:
                continue
            if _same_client_qualiit(name):
                continue  # Qualiit/Quali It tratados depois
            if _looks_like_feature_folder(name):
                ok, err = _process_folder_and_move(sp, devops, drive_id, item_id, name, year_name, None)
                if ok:
                    moved += 1
                elif err:
                    errors += 1
                    logger.warning("  [%s] Erro ao mover %s: %s", year_name, name, err)
                continue
            # Pasta que pode ser cliente (ex.: Arteb, Aurora) com subpastas
            subchildren = sp.list_folder_children(drive_id, item_id)
            subfolders = [s for s in subchildren if s.get("folder") and (s.get("name") or "").strip()]
            for subfolder in subfolders:
                sub_name = (subfolder.get("name") or "").strip()
                sub_id = subfolder.get("id")
                if not sub_name or not sub_id:
                    continue
                client_hint = normalize_client_name(name)
                ok, err = _process_folder_and_move(sp, devops, drive_id, sub_id, sub_name, year_name, client_hint)
                if ok:
                    moved += 1
                elif err:
                    errors += 1
                    logger.warning("  [%s/%s] Erro ao mover %s: %s", year_name, name, sub_name, err)
    return (moved, errors)


def main() -> int:
    try:
        devops = AzureDevOpsClient()
    except Exception as e:
        logger.error("Azure DevOps não configurado. Configure AZURE_DEVOPS_PAT no .env: %s", e)
        return 1

    sp = SharePointFileService()
    drive_id, base_id = sp.ensure_folder_path("")  # raiz = Projetos DevOps
    children = sp.list_folder_children(drive_id, base_id)
    moved = 0
    errors = 0

    for item in children:
        if not item.get("folder"):
            continue
        name = (item.get("name") or "").strip()
        if not name:
            continue
        if _is_year_folder(name):
            logger.info("Pasta de ano já no lugar: %s", name)
            continue

        # Pasta “errada” na raiz (ex.: Arteb, Aryzta)
        client_hint = normalize_client_name(name)
        logger.info("Processando pasta na raiz (cliente): %s", name)
        subchildren = sp.list_folder_children(drive_id, item["id"])
        subfolders = [c for c in subchildren if c.get("folder") and (c.get("name") or "").strip()]

        for sub in subfolders:
            sub_name = (sub.get("name") or "").strip()
            sub_id = sub.get("id")
            if not sub_name or not sub_id:
                continue
            try:
                wi = devops.resolve_feature_for_folder_name(sub_name, client_hint)
                if wi:
                    info = work_item_to_feature_info(wi)
                    path = feature_info_to_folder_path(info)
                    rel = path.relative_path()  # ex.: 2026/Arteb/16526 - 025571-02 - Arteb - Quadro...
                    parent_rel = "/".join(rel.split("/")[:-1])  # 2026/Arteb
                    canonical_name = path.folder_name
                else:
                    parent_rel = f"{FALLBACK_YEAR_FOLDER}/{name}"
                    canonical_name = sub_name

                parent_rel_sanitized = "/".join(
                    sanitize_folder_name_for_sharepoint(p) for p in parent_rel.split("/") if p.strip()
                )
                _d, dest_parent_id = sp.ensure_folder_path(parent_rel_sanitized)
                name_para_sharepoint = sanitize_folder_name_for_sharepoint(canonical_name)
                # Evita 409: não move se já existe pasta com nome canônico no destino
                existing = sp.list_folder_children(drive_id, dest_parent_id)
                name_lower = (name_para_sharepoint or "").strip().lower()
                if any(
                    c.get("folder") and (c.get("name") or "").strip().lower() == name_lower
                    for c in existing
                ):
                    logger.info("  Pasta já existe em %s/%s, ignorando: %s", parent_rel, canonical_name, sub_name)
                else:
                    try:
                        sp.move_item(drive_id, sub_id, dest_parent_id, new_name=name_para_sharepoint)
                        moved += 1
                        logger.info("  Movido: %s -> %s/%s", sub_name, parent_rel, canonical_name)
                    except Exception as ex:
                        if "409" in str(ex) or "Conflict" in str(ex):
                            logger.info("  Destino já contém pasta canônica, ignorando: %s", sub_name)
                        else:
                            errors += 1
                            logger.warning("  Erro ao mover %s: %s", sub_name, ex)
            except Exception as e:
                if "409" in str(e) or "Conflict" in str(e):
                    logger.info("  Destino já contém pasta canônica, ignorando: %s", sub_name)
                else:
                    errors += 1
                    logger.warning("  Erro ao mover %s: %s", sub_name, e)

        # Opcional: remover pasta raiz (ex.: Arteb) se ficou vazia
        if not subfolders:
            logger.info("  Nenhuma subpasta em %s", name)

    # Reorganizar conteúdo dentro de cada pasta de ano (2020-2023, 2024, 2025, 2026):
    # pastas com nome de Feature ou dentro de cliente -> consultar Azure DevOps e mover para Ano > Cliente > Feature ID - Nº Proposta - Título
    logger.info("Reorganizando conteúdo das pastas de ano (consultando Azure DevOps para ano e cliente)...")
    moved2, errors2 = _reorganize_year_folder_contents(sp, devops, drive_id, base_id)
    moved += moved2
    errors += errors2

    # Remover duplicatas em 2020-2023: pastas cuja versão canônica já existe no ano/cliente correto
    removed = _remove_duplicates_in_2020_2023(sp, devops, drive_id, base_id)
    if removed:
        logger.info("Removidas %s pasta(s) duplicadas em 2020-2023 (já existem no ano/cliente correto).", removed)

    # Mesclar Qualiit em Quali It em cada ano (mesma empresa)
    merged = _merge_qualiit_into_quali_it(sp, drive_id, base_id)
    if merged:
        logger.info("Mesclado conteúdo Qualiit -> Quali It em %s ano(s).", merged)

    logger.info("Reorganização concluída: %s pasta(s) movida(s), %s erro(s).", moved, errors)
    return 0 if errors == 0 else 1


def _remove_duplicates_in_2020_2023(
    sp: SharePointFileService,
    devops: AzureDevOpsClient,
    drive_id: str,
    base_id: str,
) -> int:
    """
    Percorre apenas a pasta 2020-2023. Para cada subpasta (ou subpasta de cliente),
    resolve a Feature no Azure DevOps; se a pasta canônica (Feature ID - Nº Proposta - Título)
    já existir no ano/cliente correto (ex.: 2025/Belliz/...), remove a pasta em 2020-2023 (duplicata).
    Retorna a quantidade de pastas removidas.
    """
    children = sp.list_folder_children(drive_id, base_id)
    folder_2020_2023_id = None
    for c in children:
        if c.get("folder") and (c.get("name") or "").strip() == FALLBACK_YEAR_FOLDER:
            folder_2020_2023_id = c["id"]
            break
    if not folder_2020_2023_id:
        return 0

    removed = 0
    sub = sp.list_folder_children(drive_id, folder_2020_2023_id)
    # Processar pastas diretas (feature-like) e pastas de cliente (ex.: Belliz) com suas subpastas
    to_check: list[tuple[str, str, str | None]] = []  # (folder_id, folder_name, client_hint)
    for item in sub:
        if not item.get("folder"):
            continue
        name = (item.get("name") or "").strip()
        item_id = item.get("id")
        if not name or not item_id:
            continue
        if _same_client_qualiit(name):
            continue
        if _looks_like_feature_folder(name):
            to_check.append((item_id, name, None))
        else:
            # Pasta de cliente (ex.: Belliz, Arteb)
            subchildren = sp.list_folder_children(drive_id, item_id)
            for subitem in subchildren:
                if not subitem.get("folder"):
                    continue
                subname = (subitem.get("name") or "").strip()
                subid = subitem.get("id")
                if not subname or not subid:
                    continue
                to_check.append((subid, subname, normalize_client_name(name)))

    for folder_id, folder_name, client_hint in to_check:
        try:
            wi = devops.resolve_feature_for_folder_name(folder_name, client_hint)
            if not wi:
                continue
            info = work_item_to_feature_info(wi)
            path = feature_info_to_folder_path(info)
            rel = path.relative_path()
            # Só remove se a pasta canônica estiver em outro ano (não em 2020-2023)
            if rel.startswith(FALLBACK_YEAR_FOLDER + "/"):
                continue
            # Verificar se a pasta canônica já existe no destino
            canonical_exists = sp.get_folder_id_by_relative_path(drive_id, rel) is not None
            if not canonical_exists:
                continue
            sp.delete_item(drive_id, folder_id)
            removed += 1
            logger.info(
                "  [2020-2023] Removida duplicata (já existe em %s): %s",
                rel,
                folder_name,
            )
        except Exception as e:
            logger.debug("  [2020-2023] Ao verificar duplicata %s: %s", folder_name, e)

    return removed


def _merge_qualiit_into_quali_it(sp: SharePointFileService, drive_id: str, base_id: str) -> int:
    """
    Em cada pasta de ano sob base_id, se existirem 'Qualiit' e 'Quali It',
    move todo o conteúdo de Qualiit para Quali It e remove a pasta Qualiit vazia.
    Retorna a quantidade de anos em que a mesclagem foi feita.
    """
    years_done = 0
    children = sp.list_folder_children(drive_id, base_id)
    for item in children:
        if not item.get("folder"):
            continue
        name = (item.get("name") or "").strip()
        if not name or not _is_year_folder(name):
            continue
        year_name = name
        year_id = item["id"]
        sub = sp.list_folder_children(drive_id, year_id)
        source_id = None
        target_id = None
        for c in sub:
            if not c.get("folder"):
                continue
            n = (c.get("name") or "").strip()
            role = _same_client_qualiit(n)
            if role == "source":
                source_id = c["id"]
            elif role == "target":
                target_id = c["id"]
        if not source_id or not target_id:
            continue
        # Move todos os itens de Qualiit para Quali It
        qualiit_children = sp.list_folder_children(drive_id, source_id)
        for child in qualiit_children:
            cid = child.get("id")
            cname = (child.get("name") or "").strip()
            if not cid or not cname:
                continue
            try:
                sp.move_item(drive_id, cid, target_id, new_name=None)  # mantém o nome
                logger.info("  [%s] Qualiit -> Quali It: %s", year_name, cname)
            except Exception as e:
                logger.warning("  [%s] Erro ao mover %s para Quali It: %s", year_name, cname, e)
        try:
            sp.delete_item(drive_id, source_id)
            logger.info("  [%s] Pasta Qualiit vazia removida.", year_name)
        except Exception as e:
            logger.warning("  [%s] Erro ao remover pasta Qualiit: %s", year_name, e)
        years_done += 1
    return years_done


if __name__ == "__main__":
    sys.exit(main())
