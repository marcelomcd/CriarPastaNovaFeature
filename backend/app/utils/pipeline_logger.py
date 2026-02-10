"""
Log estruturado da pipeline FluxoNovasFeatures.
Registra por Feature: Cliente, Feature ID, Número Proposta, Título, anexos, links.
Saída: HTML em backend/logs/pipeline_YYYYMMDD_HHMMSS.html (um arquivo por execução).
"""
import html
import logging
from datetime import datetime
from pathlib import Path

from app.config import settings

_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
LOGS_DIR = _BACKEND_DIR / "logs"
LOG_PREFIX = "pipeline"

logger = logging.getLogger(__name__)

# Arquivo HTML da execução atual (preenchido por start_html_log, fechado por end_html_log)
_html_log_path: Path | None = None


def _html_log_file_path() -> Path:
    """Arquivo de log HTML desta execução."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    return LOGS_DIR / f"{LOG_PREFIX}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"


def _feature_url(work_item_id: int) -> str:
    """URL do work item no Azure DevOps."""
    org = settings.AZURE_DEVOPS_ORG
    if org.startswith("$(") and org.endswith(")"):
        org = "qualiit"
    proj = (settings.AZURE_DEVOPS_PROJECT or "").strip()
    if "%" in proj:
        from urllib.parse import unquote
        proj = unquote(proj)
    from urllib.parse import quote
    proj_enc = quote(proj, safe="", encoding="utf-8")
    return f"https://dev.azure.com/{org}/{proj_enc}/_workitems/edit/{work_item_id}"


def _html_header(title: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 24px; background: #f5f5f5; }}
    h1 {{ color: #0078d4; margin-bottom: 8px; }}
    .meta {{ color: #666; margin-bottom: 20px; font-size: 14px; }}
    table {{ border-collapse: collapse; width: 100%; max-width: 1200px; background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,.08); border-radius: 8px; overflow: hidden; }}
    th {{ background: #0078d4; color: #fff; text-align: left; padding: 12px 14px; font-size: 13px; }}
    td {{ padding: 12px 14px; border-bottom: 1px solid #eee; font-size: 13px; vertical-align: top; }}
    tr:hover {{ background: #f9f9f9; }}
    tr.erro {{ background: #fdecea; }}
    tr.erro:hover {{ background: #fad4cf; }}
    a {{ color: #0078d4; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .anexos {{ max-width: 220px; word-break: break-word; }}
    .erro-cell {{ color: #a4262c; font-weight: 500; }}
  </style>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  <p class="meta">Execução: {html.escape(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))}</p>
  <table>
    <thead>
      <tr>
        <th>Feature ID</th>
        <th>Cliente</th>
        <th>Proposta</th>
        <th>Título</th>
        <th>Anexos</th>
        <th>Pasta SharePoint</th>
        <th>Link Feature</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
"""


def start_html_log() -> Path | None:
    """
    Inicia o log HTML desta execução (cria arquivo com cabeçalho e tabela).
    Deve ser chamado no início da pipeline; retorna o path do arquivo ou None em caso de erro.
    """
    global _html_log_path
    try:
        path = _html_log_file_path()
        with open(path, "w", encoding="utf-8") as f:
            f.write(_html_header("Log da Pipeline – Fluxo Novas Features"))
        _html_log_path = path
        logger.info("Log HTML iniciado: %s", path.name)
        return path
    except OSError as e:
        logger.warning("Não foi possível criar log HTML: %s", e)
        return None


def end_html_log() -> None:
    """Fecha o log HTML (escreve rodapé e fecha o arquivo). Deve ser chamado ao final da pipeline."""
    global _html_log_path
    if not _html_log_path:
        return
    try:
        with open(_html_log_path, "a", encoding="utf-8") as f:
            f.write("    </tbody>\n  </table>\n</body>\n</html>\n")
        logger.info("Log HTML fechado: %s", _html_log_path.name)
    except OSError as e:
        logger.warning("Não foi possível fechar log HTML: %s", e)
    _html_log_path = None


def log_feature_result(
    *,
    work_item_id: int,
    cliente: str,
    numero_proposta: str | None,
    titulo: str,
    anexos_adicionados: list[str],
    link_pasta_sharepoint: str,
    link_feature: str | None = None,
    erro: str | None = None,
) -> None:
    """
    Escreve um bloco de log para uma Feature processada.
    Saída: console (logger) e, se start_html_log foi chamado, uma linha no log HTML.
    """
    link_feature = link_feature or _feature_url(work_item_id)
    proposta = (numero_proposta or "").strip() or "N/A"
    anexos_str = ", ".join(anexos_adicionados) if anexos_adicionados else "Nenhum"

    # Console / pipeline
    logger.info(
        "Feature %s | Cliente: %s | Proposta: %s | Título: %s | Anexos: %s | SharePoint: %s | Link: %s",
        work_item_id, cliente, proposta, titulo, anexos_str, link_pasta_sharepoint, link_feature,
    )
    if erro:
        logger.error("Feature %s erro: %s", work_item_id, erro)

    # HTML (se log foi iniciado)
    if _html_log_path:
        try:
            row_class = "erro" if erro else ""
            status = f'<span class="erro-cell">{html.escape(erro)}</span>' if erro else "OK"
            link_wi = f'<a href="{html.escape(link_feature)}" target="_blank" rel="noopener">#{work_item_id}</a>'
            link_sp = f'<a href="{html.escape(link_pasta_sharepoint)}" target="_blank" rel="noopener">Abrir</a>' if link_pasta_sharepoint and link_pasta_sharepoint != "—" else "—"
            with open(_html_log_path, "a", encoding="utf-8") as f:
                f.write(
                    f'    <tr class="{row_class}">\n'
                    f'      <td>{link_wi}</td>\n'
                    f'      <td>{html.escape(cliente)}</td>\n'
                    f'      <td>{html.escape(proposta)}</td>\n'
                    f'      <td>{html.escape(titulo)}</td>\n'
                    f'      <td class="anexos">{html.escape(anexos_str)}</td>\n'
                    f'      <td>{link_sp}</td>\n'
                    f'      <td><a href="{html.escape(link_feature)}" target="_blank" rel="noopener">Abrir</a></td>\n'
                    f'      <td>{status}</td>\n'
                    f'    </tr>\n'
                )
        except OSError as e:
            logger.warning("Não foi possível escrever linha no log HTML: %s", e)
