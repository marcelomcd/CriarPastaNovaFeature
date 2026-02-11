# Instruções para configurar a Pipeline (FluxoNovasFeatures)

Há **duas pipelines** no Azure Repos:

1. **Pipeline principal** (`azure-pipelines.yml`): varredura de Features, criação de pastas no SharePoint, link no work item e sincronização de anexos. **Agendada para toda segunda-feira às 05:00** (horário de Brasília).
2. **Pipeline de organização** (`azure-pipelines-organize.yml`): reorganização estrutural da pasta Projetos DevOps (Ano > Cliente > Feature, mesclar Qualiit → Quali It, remover duplicatas em 2020-2023). **Sem agendamento** — executar **somente quando houver necessidade** de organizar a pasta principal.

Use os **mesmos nomes e valores** do arquivo `backend/.env` (ou do modelo `backend/.env.example`) ao criar as variáveis em **Pipelines → Variables**. Nunca commite o `.env`.

---

## 1. Referência de variáveis

O arquivo **`backend/.env.example`** contém as variáveis da pipeline principal. Copie para `backend/.env`, preencha os valores e use os **mesmos nomes** no Azure DevOps (**Variables** → **+ New variable**). Para as marcadas como **Secreto**, marque **Keep this value secret**.

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

**Opcionais:** `LOG_LEVEL`, `PIPELINE_FULL_SCAN`, `PIPELINE_ONLY_CLOSED` — ver seção [Comportamento e opcionais](#comportamento-e-opcionais).

---

## 2. Criar e configurar a Pipeline

### 2.1 Criar a pipeline principal

1. Acesse o projeto no Azure DevOps (ex.: `https://dev.azure.com/qualiit/ALM`).
2. **Pipelines** → **Pipelines** → **New pipeline** (ou **Create Pipeline**).
3. **Azure Repos Git** → repositório do projeto (ex.: **Qualiit.FluxoNovasFeatures**).
4. **Existing Azure Pipelines YAML file** → Branch: `main` (ou `master`) → Path: **`/azure-pipelines.yml`**.
5. **Continue** (não clique em Run ainda).

**Pipeline de organização (opcional):** para criar a pipeline secundária (reorganização sob demanda), repita o processo escolhendo Path: **`/azure-pipelines-organize.yml`**. Use as mesmas variáveis; essa pipeline **não tem agendamento** e deve ser executada apenas quando for necessário reorganizar a pasta Projetos DevOps.

### 2.2 Definir as variáveis

1. Na tela da pipeline, clique em **Edit** e no canto superior direito em **Variables**.
2. **+ New variable** para cada variável da tabela acima; use os valores do seu `backend/.env`.
3. Para `AZURE_DEVOPS_PAT` e `SHAREPOINT_CLIENT_SECRET`, marque **Keep this value secret**.
4. **Save**.

### 2.3 Rodar a pipeline

1. **Run pipeline** → confirme o branch → **Run**.
2. O passo **"Executar varredura (pastas + link + anexos)"** processa as Features (Area Path: Quali IT ! Gestao de Projetos): na **primeira execução** (ou com `PIPELINE_FULL_SCAN=1`) processa todas; nas **execuções seguintes** processa apenas Features **novas ou alteradas** (novas Features, Closed, novos anexos).
3. Ao final, o artefato **logs** pode ser baixado (pasta `backend/logs`). O log da execução é um arquivo **HTML** (`pipeline_YYYYMMDD_HHMMSS.html`).

Com isso, o SharePoint fica organizado: Features **encerradas** em **Ano/Closed/Cliente/Feature**; as demais em **Ano/Cliente/Feature**.

---

## 3. Comportamento e opcionais

- **Timeout:** o job tem **120 minutos** (em vez do padrão 60).
- **SharePoint 503:** retry com backoff em 502/503/504 (até 3 tentativas).
- **Azure DevOps 400:** se a atualização do campo `Custom.LinkPastaDocumentacao` falhar por validação (campos obrigatórios vazios), a pipeline **não falha**; a pasta e os anexos já foram garantidos no SharePoint; o link fica apenas não gravado no work item (registrado em log). Para itens que falharem por outro motivo (ex.: 503), um segundo passo reprocessa apenas pasta e anexos (sem atualizar o work item).

**Variáveis opcionais:**

- **`LOG_LEVEL`** — O YAML já define `INFO`; crie só se quiser outro nível (ex.: `DEBUG`).
- **`PIPELINE_FULL_SCAN`** — Use `1` ou `true` para: (a) primeira execução cancelada/falhou antes do fim; (b) preencher lacunas; (c) forçar varredura completa. Em modo completo, a lógica continua sendo *só criar o que falta* (sem duplicar pastas nem anexos).
- **`PIPELINE_ONLY_CLOSED`** — Mantenha **desligado** (padrão) para incluir **novas Features** (principal), atualizações para Closed e novos anexos. Use `1` só em runs pontuais em que queira processar *exclusivamente* Features Encerradas (exclui novas Features).

---

## 4. Modo atualização: não recria tudo

A pipeline **só atualiza o que falta**; não recria pastas nem reenvia anexos que já existem:

- **Pastas:** criadas somente quando ainda não existem para aquela Feature.
- **Anexos:** incluídos somente os que ainda não estão na pasta (sem duplicar).
- **Link:** atualizado no work item apenas quando o valor for diferente.
- **Closed:** quando a Feature passa para Status Closed (Encerrado), o conteúdo da pasta é movido para **Ano/Closed/Cliente/Feature**.

Para preencher lacunas após erros, execute **uma vez** com **`PIPELINE_FULL_SCAN=1`**.

---

## 5. Agendamento semanal (pipeline principal)

A pipeline principal está configurada para rodar **toda segunda-feira às 05:00** (horário de Brasília). Varredura **incremental** processa:

1. **Novas Features** (criação) — principal.
2. **Atualizações para Features com Status Closed** (encerradas; pastas movidas para Closed).
3. **Inclusão de novos anexos** (Features alteradas desde a última execução).

A consulta usa a data da última execução (`last_run`). Com **`PIPELINE_ONLY_CLOSED`** em branco ou `0` (padrão), novas Features são sempre incluídas. Após a varredura completa inicial, o uso semanal tende a ser rápido (poucas novas Features, anexos e movimentações para Closed).

- **Primeira execução:** rode **manualmente** (Run pipeline); não há cache ainda, então a varredura é completa.
- **Execuções seguintes:** a pipeline roda no agendamento e processa só o que mudou.

---

## 6. Estrutura de pastas no SharePoint

- **Pasta base:** Documentações de Projetos > **Projetos DevOps** — [Abrir Projetos DevOps](https://qualiitcombr.sharepoint.com/sites/projetosqualiit/Documentos%20Compartilhados/Forms/AllItems.aspx?id=%2Fsites%2Fprojetosqualiit%2FDocumentos%20Compartilhados%2FProjetos%20DevOps)
- **Dentro de Projetos DevOps:** **Ano** > **Cliente** (ou **Closed**) > **Feature ID - Nº Proposta - Título**

Defina **`SHAREPOINT_FOLDER_PATH_BASE=Projetos DevOps`** (só o nome da pasta; incluir o nome da biblioteca faz a API criar a pasta em duplicidade).

---

## 7. Execução local

Para rodar **varredura** e/ou **consolidação** no seu computador (evitando consumo no Azure Repos), use o arquivo **`run_pipelines_local.bat`** na raiz do projeto (não versionado; ver `.gitignore`). Ele oferece:

- **Opção 1 — Varredura:** mesmo que a pipeline principal (Features + pastas + link + anexos); abre a pasta `backend/logs` com o log HTML ao final.
- **Opção 2 — Consolidar:** move as pastas de origem (Documentação dos Clientes, Documentação dos Projetos, Projetos DevOps OLD, TestePowerAutomate) para **Projetos DevOps**. Para funcionar, defina no **`backend/.env`** a variável **`SHAREPOINT_SOURCE_FOLDER_PATHS`** com o valor:  
  `Documentação dos Clientes;Documentação dos Projetos;Projetos DevOps OLD;TestePowerAutomate`
- **Opção 3 — Ambos:** executa primeiro a varredura e depois a consolidação (útil para fazer a consolidação das pastas e em seguida garantir que todas as Features tenham pasta e anexos).

No Azure Repos permanece apenas a pipeline principal (varredura semanal). A consolidação é feita localmente quando necessário.
