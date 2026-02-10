# Configurar a Pipeline (FluxoNovasFeatures)

Use os **mesmos valores** do seu `backend/.env` ao configurar no Azure DevOps. Nunca commite o `.env`.

---

## Variáveis da pipeline

Configure estas variáveis em **Pipelines** → sua pipeline → **Edit** → **Variables** (canto superior direito). Para as marcadas como **Secreto**, marque **Keep this value secret**.

| Nome | Descrição | Secreto? |
|------|-----------|----------|
| `AZURE_DEVOPS_PAT` | Personal Access Token do Azure DevOps (Work Items Read & Write) | **Sim** |
| `AZURE_DEVOPS_ORG` | Organização (ex.: qualiit) | Não |
| `AZURE_DEVOPS_PROJECT` | Nome do projeto (ex.: Quali IT - Inovação e Tecnologia) | Não |
| `SHAREPOINT_CLIENT_ID` | Client ID do app no Entra ID (SharePoint/Graph) | Não |
| `SHAREPOINT_CLIENT_SECRET` | Client Secret do app | **Sim** |
| `SHAREPOINT_TENANT_ID` | Tenant ID (Diretório) do Entra ID | Não |
| `SHAREPOINT_SITE_URL` | URL do site SharePoint (ex.: https://qualiitcombr.sharepoint.com/sites/projetosqualiit) | Não |
| `SHAREPOINT_FOLDER_PATH_BASE` | Caminho base da biblioteca (ex.: Documentos Compartilhados/Projetos DevOps) | Não |

Opcionais: `LOG_LEVEL` = `INFO`; `PIPELINE_FULL_SCAN` = `1` ou `true` para forçar **varredura completa** (use na 1ª execução manual ou para reparo; se não definir, após a primeira execução a pipeline faz só **varredura incremental** — novas Features ou alterações em anexos).

---

## Como configurar e executar a pipeline manualmente

### 1. Criar a pipeline

1. Acesse o projeto no Azure DevOps (ex.: `https://dev.azure.com/qualiit/ALM`).
2. **Pipelines** → **Pipelines** → **New pipeline** (ou **Create Pipeline**).
3. **Azure Repos Git** → repositório **Qualiit.FluxoNovasFeatures**.
4. **Existing Azure Pipelines YAML file** → Branch: `main` (ou `master`) → Path: `/azure-pipelines.yml`.
5. **Continue** (não clique em Run ainda).

### 2. Definir as variáveis

1. Na tela da pipeline, clique em **Edit** e no canto superior direito em **Variables**.
2. **+ New variable** para cada linha da tabela acima; use os valores do seu `backend/.env`.
3. **Save**.

### 3. Rodar a pipeline

1. **Run pipeline** → confirme o branch → **Run**.
2. O passo **"Executar varredura (pastas + link + anexos)"** processa as Features (Area Path: Quali IT ! Gestao de Projetos): na **primeira execução** (ou com `PIPELINE_FULL_SCAN=1`) processa todas; nas **execuções seguintes** processa apenas Features **novas ou alteradas** (ex.: novo anexo), graças ao cache da data da última execução.
3. Ao final, o artefato **logs** pode ser baixado (pasta `backend/logs`). O log da execução é um arquivo **HTML** (`pipeline_YYYYMMDD_HHMMSS.html`) para leitura fácil no navegador.

Com isso, o SharePoint fica organizado: Features **encerradas** em **Ano/Closed/Cliente/Feature**; as demais em **Ano/Cliente/Feature**. Não há pastas nem anexos duplicados. Para rodar de novo, execute a pipeline manualmente ou use os Service Hooks após a primeira execução.

---

## Gatilhos: somente após a primeira execução manual

- **Primeira execução:** rode a pipeline **manualmente** (Run pipeline). Não há agendamento (cron) nem trigger em push.
- **Depois da primeira execução:** desbloqueie os gatilhos configurando **Service Hooks** no Azure DevOps:
  - **Project Settings** → **Service hooks** → **Create subscription**
  - Eventos: **Work item created** e **Work item updated** (novas Features e anexos adicionados/atualizados).
  - URL: `https://<sua-api>/webhook/devops` (API FastAPI publicada).
  - Header: `X-Webhook-Secret` = valor de `WEBHOOK_SECRET`.

Assim, apenas **novas Features criadas** e **anexos adicionados/atualizados** disparam processamento (via API); a pipeline em YAML continua sendo executada só manualmente quando quiser refazer varredura completa.
