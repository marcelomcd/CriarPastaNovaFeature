# Variáveis das pipelines e da API (FluxoNovasFeatures)

Use os **mesmos valores** do seu `.env` local quando configurar no Azure DevOps. Nunca commite o `.env`.

---

## API FastAPI (webhook + varredura)

A API consome as mesmas variáveis abaixo. Em produção, configure-as como variáveis de ambiente do App Service/Container Apps ou via Key Vault.

| Variável | Descrição | Secreto? |
|----------|-----------|----------|
| `AZURE_DEVOPS_PAT` | Personal Access Token do Azure DevOps | Sim |
| `AZURE_DEVOPS_ORG` | Organização (ex.: qualiit) | Não |
| `AZURE_DEVOPS_PROJECT` | Nome do projeto (ex.: Quali IT - Inovação e Tecnologia) | Não |
| `SHAREPOINT_CLIENT_ID` | Client ID do app no Entra ID (SharePoint/Graph) | Não |
| `SHAREPOINT_CLIENT_SECRET` | Client Secret do app | Sim |
| `SHAREPOINT_TENANT_ID` | Tenant ID do Entra ID | Não |
| `SHAREPOINT_SITE_URL` | URL do site SharePoint (ex.: https://qualiitcombr.sharepoint.com/sites/projetosqualiit) | Não |
| `SHAREPOINT_FOLDER_PATH_BASE` | Caminho base da biblioteca (ex.: Documentos Compartilhados/Projetos DevOps) | Não |
| `WEBHOOK_SECRET` | Secret para validar requisições do Service Hook | Sim |

Opcionais: `LOG_LEVEL`, `CLOSED_FEATURES_ONEDRIVE_PATH` (para módulo de fechamento).

---

## Pipeline de varredura (azure-pipelines.yml)

| Variável no Azure DevOps | Valor (origem) | Secreto? |
|--------------------------|----------------|----------|
| `AZURE_DEVOPS_PAT` | Do `.env` | Sim |
| `SHAREPOINT_CLIENT_ID` | Do `.env` | Não |
| `SHAREPOINT_CLIENT_SECRET` | Do `.env` | Sim |
| `SHAREPOINT_TENANT_ID` | Do `.env` | Não |
| `SHAREPOINT_SITE_URL` | Do `.env` | Não |
| `SHAREPOINT_FOLDER_PATH_BASE` | Do `.env` | Não |
| `AZURE_DEVOPS_ORG` | Do `.env` (ex.: qualiit) | Não |
| `AZURE_DEVOPS_PROJECT` | Do `.env` | Não |

---

## Service Hooks (Azure DevOps → FastAPI)

No Azure DevOps: **Project Settings** → **Service hooks** → **Create subscription**:

1. **Work item created**: filtro por Work Item Type = Feature e Area Path do projeto.
2. **Work item updated**: filtro por Work Item Type = Feature.

URL do webhook: `https://<sua-api>/webhook/devops`. Inclua o `WEBHOOK_SECRET` no header (ex.: `X-Webhook-Secret`) ou no body conforme implementação.

---

## Como configurar no Azure DevOps

1. **Pipelines** → Editar pipeline → **Variables**.
2. **+ New variable** para cada variável; marque **Keep this value secret** para as marcadas como Sim.
3. **Save**.

Para a API em Azure: configure em **App Service** → Configuration → Application settings (ou Key Vault references).
