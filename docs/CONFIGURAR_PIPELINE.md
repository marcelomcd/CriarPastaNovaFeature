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

Opcional: `LOG_LEVEL` = `INFO` (o YAML já define valor padrão se não informado).

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
2. O passo **"Executar varredura (pastas + link + anexos)"** lista todas as Features (Area Path: Quali IT ! Gestao de Projetos), cria a pasta de cada uma no SharePoint, preenche `Custom.LinkPastaDocumentacao` e sincroniza os anexos.
3. Ao final, o artefato **logs** pode ser baixado (se `backend/logs` tiver sido gerado).

Com isso, o SharePoint fica organizado com todas as Features atuais. Para rodar de novo (ex.: após novas Features ou anexos), execute a pipeline manualmente outra vez ou aguarde a execução agendada.

---

## Gatilhos já definidos no YAML

O arquivo `azure-pipelines.yml` já está configurado com:

- **trigger: none** — a pipeline não dispara em todo push; só manual ou agendada.
- **schedules** — varredura diária (ex.: 10:00 UTC). Assim, após a primeira execução manual, as próximas rodam no agendamento e mantêm pastas e anexos alinhados.

Para **tempo real** (nova Feature ou anexo assim que for criado/alterado), é necessário publicar a API FastAPI e configurar **Service Hooks** no Azure DevOps (**Project Settings** → **Service hooks**): eventos **Work item created** e **Work item updated**, URL `https://<sua-api>/webhook/devops`, header `X-Webhook-Secret` com o valor de `WEBHOOK_SECRET`.
