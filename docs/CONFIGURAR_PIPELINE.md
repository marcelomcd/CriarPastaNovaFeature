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

**Variáveis opcionais (não obrigatórias para a 1ª execução):**

- **`LOG_LEVEL`** — O YAML já define `INFO`; só crie essa variável se quiser outro nível (ex.: `DEBUG`).
- **`PIPELINE_FULL_SCAN`** — Na **primeira** execução não é preciso: como ainda não existe cache, a varredura já é **completa**. Use `1` ou `true` para: (a) primeira execução **cancelada/falhou** antes do fim; (b) **preencher lacunas** (criar pastas e incluir anexos que faltaram em runs anteriores); (c) forçar varredura completa em qualquer execução. Em modo completo, a lógica continua sendo *só criar o que falta* (sem duplicar pastas nem anexos).

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

Com isso, o SharePoint fica organizado: Features **encerradas** em **Ano/Closed/Cliente/Feature**; as demais em **Ano/Cliente/Feature**.

---

## Modo atualização: não recria tudo

A pipeline **só atualiza o que falta**; não recria pastas nem reenvia anexos que já existem:

- **Pastas:** são **criadas somente** quando ainda não existem para aquela Feature. Se a pasta já existir, ela é reutilizada.
- **Anexos:** são **incluídos somente** os que ainda não estão na pasta. Arquivos já existentes (mesmo nome) são ignorados, sem duplicar.
- **Link:** o campo `Custom.LinkPastaDocumentacao` no Azure DevOps é atualizado apenas quando o valor for diferente.

Assim, rodar a pipeline de novo (incremental ou com varredura completa) **não gera duplicidade**. Para preencher lacunas após erros (pastas ou anexos que não foram criados na primeira vez), execute **uma vez** com **`PIPELINE_FULL_SCAN=1`**: todas as Features serão processadas e, para cada uma, só o que faltar será criado ou incluído.

---

## Agendamento diário (5:00 da manhã)

A pipeline está configurada para rodar **todo dia às 5:00 (horário de Brasília)**, sincronizando o que foi feito no dia anterior. Ela **não varre** toda a estrutura do Azure DevOps nem do SharePoint: usa varredura **incremental**, processando apenas:

- **Novas Features** (criação)
- **Features com anexos adicionados ou atualizados**
- **Features encerradas** (movidas para a pasta Closed)

A consulta usa a data da última execução (`last_run`): só são buscadas Features cuja revisão (System.ChangedDate) seja posterior a essa data.

- **Primeira execução:** rode **manualmente** (Run pipeline); não há cache ainda, então a varredura é completa.
- **Execuções seguintes:** às 5:00 da manhã a pipeline roda sozinha e processa só o que mudou (novas Features, anexos, Closed).

---

## Pipeline Consolidar SharePoint

- **Consolidar SharePoint** (`azure-pipelines-consolidate.yml`): move documentos de várias pastas (URLs de compartilhamento) para a pasta do projeto, na mesma estrutura (Projetos DevOps > Ano > Cliente > Feature...), sem duplicar arquivos.

Variáveis e uso: **[PIPELINES_RETRY_E_CONSOLIDAR.md](PIPELINES_RETRY_E_CONSOLIDAR.md)**.

A **pipeline principal** faz um segundo passo automático para os itens que falharam: reprocessa apenas pasta e anexos (sem atualizar o work item), para que mesmo Features com erro 400 (campos obrigatórios) tenham pasta e anexos no SharePoint.

---

## Estrutura de pastas (uma subpasta só)

Para que a raiz seja **Documentações de Projetos > Projetos DevOps** (sem a camada "Documentos Compartilhados"), defina **`SHAREPOINT_FOLDER_PATH_BASE=Projetos DevOps`** nas variáveis da pipeline e no `.env`.
