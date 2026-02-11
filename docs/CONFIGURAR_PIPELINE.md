# Instruções para configurar as Pipelines

Este documento descreve como configurar as **duas pipelines** no Azure DevOps. Use os **mesmos nomes e valores** do arquivo `backend/.env` (ou do modelo `backend/.env.example`) ao criar as variáveis em **Pipelines → Variables**. Nunca commite o `.env`.

- **Pipeline principal** (`azure-pipelines.yml`): varredura de Features, criação de pastas no SharePoint, link no work item e sincronização de anexos.
- **Pipeline Consolidar** (`azure-pipelines-consolidate.yml`): unificação de documentos de várias pastas de origem para a pasta **Projetos DevOps**.

Detalhes da pipeline Consolidar e estrutura de pastas: [PIPELINES_RETRY_E_CONSOLIDAR.md](PIPELINES_RETRY_E_CONSOLIDAR.md).

---

## 1. Referência de variáveis

O arquivo **`backend/.env.example`** contém todas as variáveis necessárias para as duas pipelines. Copie para `backend/.env`, preencha os valores e use os **mesmos nomes** ao configurar no Azure DevOps (em cada pipeline, **Variables** → **+ New variable**). Para as marcadas como **Secreto**, marque **Keep this value secret**.

### Pipeline principal (obrigatórias)

| Nome | Descrição | Secreto? |
|------|-----------|----------|
| `AZURE_DEVOPS_PAT` | Personal Access Token do Azure DevOps (Work Items Read & Write) | **Sim** |
| `AZURE_DEVOPS_ORG` | Organização (ex.: qualiit) | Não |
| `AZURE_DEVOPS_PROJECT` | Nome do projeto (ex.: Quali IT - Inovação e Tecnologia) | Não |
| `SHAREPOINT_CLIENT_ID` | Client ID do app no Entra ID (SharePoint/Graph) | Não |
| `SHAREPOINT_CLIENT_SECRET` | Client Secret do app | **Sim** |
| `SHAREPOINT_TENANT_ID` | Tenant ID (Diretório) do Entra ID | Não |
| `SHAREPOINT_SITE_URL` | URL do site SharePoint (ex.: https://qualiitcombr.sharepoint.com/sites/projetosqualiit) | Não |
| `SHAREPOINT_FOLDER_PATH_BASE` | Pasta base: **Projetos DevOps** (não incluir nome da biblioteca) | Não |

**Opcionais (principal):** `LOG_LEVEL`, `PIPELINE_FULL_SCAN`, `PIPELINE_ONLY_CLOSED` — ver seção [Comportamento e opcionais](#comportamento-e-opcionais).

### Pipeline Consolidar (obrigatórias)

Além das variáveis **SharePoint** acima (`SHAREPOINT_CLIENT_ID`, `SHAREPOINT_CLIENT_SECRET`, `SHAREPOINT_TENANT_ID`, `SHAREPOINT_SITE_URL`, `SHAREPOINT_FOLDER_PATH_BASE`), defina **uma** das duas:

| Nome | Descrição | Secreto? |
|------|-----------|----------|
| `SHAREPOINT_SOURCE_FOLDER_PATHS` | Caminhos na biblioteca separados por **;** (recomendado). Ex.: `Documentação dos Clientes;Documentação dos Projetos;Projetos DevOps OLD;TestePowerAutomate` | Não |
| `SHAREPOINT_SOURCE_FOLDER_URLS` | URLs de compartilhamento das pastas de origem, separadas por **;** (alternativa) | Não |

A pipeline Consolidar **não** usa `AZURE_DEVOPS_PAT` (apenas SharePoint).

---

## 2. Criar e configurar a Pipeline principal

### 2.1 Criar a pipeline

1. Acesse o projeto no Azure DevOps (ex.: `https://dev.azure.com/qualiit/ALM`).
2. **Pipelines** → **Pipelines** → **New pipeline** (ou **Create Pipeline**).
3. **Azure Repos Git** → repositório do projeto (ex.: **Qualiit.FluxoNovasFeatures**).
4. **Existing Azure Pipelines YAML file** → Branch: `main` (ou `master`) → Path: **`/azure-pipelines.yml`**.
5. **Continue** (não clique em Run ainda).

### 2.2 Definir as variáveis (Principal)

1. Na tela da pipeline, clique em **Edit** e no canto superior direito em **Variables**.
2. **+ New variable** para cada variável da tabela “Pipeline principal (obrigatórias)” acima; use os valores do seu `backend/.env`.
3. Para `AZURE_DEVOPS_PAT` e `SHAREPOINT_CLIENT_SECRET`, marque **Keep this value secret**.
4. **Save**.

### 2.3 Rodar a pipeline principal

1. **Run pipeline** → confirme o branch → **Run**.
2. O passo **"Executar varredura (pastas + link + anexos)"** processa as Features (Area Path: Quali IT ! Gestao de Projetos): na **primeira execução** (ou com `PIPELINE_FULL_SCAN=1`) processa todas; nas **execuções seguintes** processa apenas Features **novas ou alteradas** (novas Features, Closed, novos anexos).
3. Ao final, o artefato **logs** pode ser baixado (pasta `backend/logs`). O log da execução é um arquivo **HTML** (`pipeline_YYYYMMDD_HHMMSS.html`).

Com isso, o SharePoint fica organizado: Features **encerradas** em **Ano/Closed/Cliente/Feature**; as demais em **Ano/Cliente/Feature**.

---

## 3. Criar e configurar a Pipeline Consolidar

### 3.1 Criar a pipeline

1. **Pipelines** → **Pipelines** → **New pipeline**.
2. **Azure Repos Git** → mesmo repositório.
3. **Existing Azure Pipelines YAML file** → Branch: `main` (ou `master`) → Path: **`/azure-pipelines-consolidate.yml`**.
4. **Continue** (não clique em Run ainda).

### 3.2 Definir as variáveis (Consolidar)

1. **Edit** → **Variables**.
2. Crie as variáveis **SharePoint** (mesmas da pipeline principal): `SHAREPOINT_CLIENT_ID`, `SHAREPOINT_CLIENT_SECRET`, `SHAREPOINT_TENANT_ID`, `SHAREPOINT_SITE_URL`, `SHAREPOINT_FOLDER_PATH_BASE`.
3. Crie **uma** das duas variáveis de origem:
   - **Recomendado:** `SHAREPOINT_SOURCE_FOLDER_PATHS` com valor:  
     `Documentação dos Clientes;Documentação dos Projetos;Projetos DevOps OLD;TestePowerAutomate`
   - **Ou:** `SHAREPOINT_SOURCE_FOLDER_URLS` com as URLs de compartilhamento das pastas de origem, separadas por **;**.
4. **Save**.

### 3.3 Rodar a pipeline Consolidar

1. **Run pipeline** → **Run**.
2. O passo **"Consolidar pastas SharePoint"** copia pastas e arquivos das origens para **Projetos DevOps**, mantendo a estrutura Ano > Cliente > Feature ID - Nº - Título; arquivos já existentes no destino são ignorados.

Pastas de origem e destino estão descritas em [PIPELINES_RETRY_E_CONSOLIDAR.md](PIPELINES_RETRY_E_CONSOLIDAR.md).

---

## 4. Comportamento e opcionais (Pipeline principal)

- **Timeout:** o job tem **120 minutos** (em vez do padrão 60).
- **SharePoint 503:** retry com backoff em 502/503/504 (até 3 tentativas).
- **Azure DevOps 400:** se a atualização do campo `Custom.LinkPastaDocumentacao` falhar por validação (campos obrigatórios vazios), a pipeline **não falha**; a pasta e os anexos já foram garantidos no SharePoint; o link fica apenas não gravado no work item (registrado em log). Para itens que falharem por outro motivo (ex.: 503), um segundo passo reprocessa apenas pasta e anexos (sem atualizar o work item).

**Variáveis opcionais:**

- **`LOG_LEVEL`** — O YAML já define `INFO`; crie só se quiser outro nível (ex.: `DEBUG`).
- **`PIPELINE_FULL_SCAN`** — Use `1` ou `true` para: (a) primeira execução cancelada/falhou antes do fim; (b) preencher lacunas; (c) forçar varredura completa. Em modo completo, a lógica continua sendo *só criar o que falta* (sem duplicar pastas nem anexos).
- **`PIPELINE_ONLY_CLOSED`** — Mantenha **desligado** (padrão) para incluir **novas Features** (principal), atualizações para Closed e novos anexos. Use `1` só em runs pontuais em que queira processar *exclusivamente* Features Encerradas (exclui novas Features).

---

## 5. Modo atualização: não recria tudo (Principal)

A pipeline principal **só atualiza o que falta**; não recria pastas nem reenvia anexos que já existem:

- **Pastas:** criadas somente quando ainda não existem para aquela Feature.
- **Anexos:** incluídos somente os que ainda não estão na pasta (sem duplicar).
- **Link:** atualizado no work item apenas quando o valor for diferente.

Para preencher lacunas após erros, execute **uma vez** com **`PIPELINE_FULL_SCAN=1`**.

---

## 6. Agendamento diário (Pipeline principal)

A pipeline principal está configurada para rodar **todo dia às 5:00 (horário de Brasília)**. Varredura **incremental** processa:

1. **Novas Features** (criação) — principal.
2. **Atualizações para Features com Status Closed** (encerradas).
3. **Inclusão de novos anexos** (Features alteradas desde a última execução).

A consulta usa a data da última execução (`last_run`). Com **`PIPELINE_ONLY_CLOSED`** em branco ou `0` (padrão), novas Features são sempre incluídas.

- **Primeira execução:** rode **manualmente** (Run pipeline); não há cache ainda, então a varredura é completa.
- **Execuções seguintes:** às 5:00 a pipeline roda sozinha e processa só o que mudou.

---

## 7. Estrutura de pastas no SharePoint

- **Pasta base:** Documentações de Projetos > **Projetos DevOps** — [Abrir Projetos DevOps](https://qualiitcombr.sharepoint.com/sites/projetosqualiit/Documentos%20Compartilhados/Forms/AllItems.aspx?id=%2Fsites%2Fprojetosqualiit%2FDocumentos%20Compartilhados%2FProjetos%20DevOps)
- **Dentro de Projetos DevOps:** **Ano** > **Cliente** (ou **Closed**) > **Feature ID - Nº Proposta - Título**

Defina **`SHAREPOINT_FOLDER_PATH_BASE=Projetos DevOps`** (só o nome da pasta; incluir o nome da biblioteca faz a API criar a pasta em duplicidade).
