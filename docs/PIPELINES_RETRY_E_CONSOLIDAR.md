# Pipeline principal e estrutura de pastas

**No Azure Repos há duas pipelines:**

1. **Pipeline principal** (`azure-pipelines.yml`): varredura (novas Features, anexos, Features fechadas). **Agendamento: toda segunda-feira às 05:00** (horário de Brasília). Para configurá-la, siga **[CONFIGURAR_PIPELINE.md](CONFIGURAR_PIPELINE.md)**.
2. **Pipeline de organização** (`azure-pipelines-organize.yml`): reorganização estrutural da pasta Projetos DevOps (igual ao script local). **Sem agendamento** — executar **somente quando houver necessidade** de organizar a pasta principal.

**Importante:** a pipeline principal **não executa consolidação** nem reorganização estrutural. A consolidação de pastas é feita **apenas localmente**. A reorganização (Ano > Cliente > Feature, mesclar Qualiit, remover duplicatas em 2020-2023) pode ser feita localmente com `script_estruturar_projetos_devops_once.py` ou pela **Pipeline de organização** (sob demanda).

---

## 1. Pipeline principal (azure-pipelines.yml)

- **Somente varredura:** a pipeline verifica, em cada execução (toda segunda-feira pela manhã, conforme agendamento), as **novas Features criadas**, **anexos adicionados** e **Features fechadas** desde a última execução. Para cada uma: garante pasta no SharePoint, link no work item e sincronização de anexos; Features encerradas têm a pasta movida para **Closed**.
- **Segundo passo automático:** Se alguma Feature falhar (ex.: 400 por campos obrigatórios vazios), a pipeline reprocessa **só esses itens** em um segundo passo: cria a pasta e sincroniza os anexos **sem** atualizar o campo no work item (evita novo 400).
- **Agendamento:** toda segunda-feira às 05:00 (BRT). A pipeline **não roda** consolidação nem o script de reorganização; para reorganização sob demanda, use a **Pipeline de organização** ou o script local.

---

## 2. Estrutura de pastas no SharePoint

**Pasta base do projeto:** **Projetos DevOps**  
Ela fica em Documentos Compartilhados. Dentro dela a pipeline cria as subpastas **Ano** > **Cliente** (ou **Closed**) > **Feature ID - Nº Proposta - Título**.

- [Abrir pasta Projetos DevOps](https://qualiitcombr.sharepoint.com/sites/projetosqualiit/Documentos%20Compartilhados/Forms/AllItems.aspx?id=%2Fsites%2Fprojetosqualiit%2FDocumentos%20Compartilhados%2FProjetos%20DevOps)

**Estrutura criada dentro de Projetos DevOps:**

- **Ano** (ex.: 2025) > **Cliente** > **Feature ID - Nº Proposta - Título** (Features ativas)
- **Ano** > **Closed** > **Cliente** > **Feature ID - Nº Proposta - Título** (Features encerradas)

Configure **`SHAREPOINT_FOLDER_PATH_BASE=Projetos DevOps`** na pipeline e no `.env`. Não use o nome da biblioteca para evitar criar a pasta em duplicidade.

---

## 3. Consolidação de pastas (somente local — não roda na pipeline)

A **consolidação** (unificar as pastas de origem em **Projetos DevOps**) **não é executada na pipeline**. Ela existe para você rodar **apenas localmente**, quando quiser (por exemplo agora, para mover o conteúdo de Documentação dos Clientes, Documentação dos Projetos etc. para Projetos DevOps).

1. No **`backend/.env`**, adicione as pastas de origem (tudo será movido para **Projetos DevOps**, com resolução pelo Número da Proposta e/ou título no Azure DevOps e colocação no ano correto):
   - **`SHAREPOINT_SOURCE_FOLDER_PATHS`** = `Documentação dos Clientes;Documentação dos Projetos;Projetos DevOps OLD`  
   (inclua **Documentação dos Projetos** para consolidar também o conteúdo dessa pasta.)
2. Execute o **`run_pipelines_local.bat`** na raiz do projeto e escolha **2 (Consolidar)** ou **3 (Ambos)** — a opção 3 roda primeiro a varredura e depois a consolidação.

O script **`backend/pipeline_consolidate_sharepoint.py`** é o mesmo que rodava na antiga pipeline Consolidar; agora é chamado pelo .bat ou manualmente (`cd backend` e `python pipeline_consolidate_sharepoint.py`).

---

## 4. Reorganização (Projetos DevOps > Ano > Cliente)

Se na raiz de **Projetos DevOps** existirem pastas de empresas (ex.: Arteb, Aryzta) ou duplicatas em 2020-2023, execute a reorganização **localmente** ou pela **Pipeline de organização** (`azure-pipelines-organize.yml`).

**Local:**  
1. **Requisitos:** `backend\.env` com **AZURE_DEVOPS_PAT** e configuração do SharePoint.  
2. **Comando:** `python backend/script_estruturar_projetos_devops_once.py` (ou `cd backend` e `python script_estruturar_projetos_devops_once.py`).

**Pipeline:** em **Pipelines** → **New pipeline** → Path: **`/azure-pipelines-organize.yml`**. Rodar **somente quando houver necessidade** de organizar a pasta principal (sem agendamento).

O script / pipeline:

- Lista a raiz de Projetos DevOps; para pastas que **não** são ano (ex.: Arteb, Aryzta), move subpastas para **Ano > Cliente > Feature ID - Nº Proposta - Título** (resolução no Azure DevOps).
- Se não for possível obter a Feature, mantém em **2020-2023 > Cliente** (ou Unknown).
- **Mesma empresa:** em cada ano, mescla **Qualiit** em **Quali It** e remove a pasta Qualiit vazia.
- **Duplicatas em 2020-2023:** remove pastas em 2020-2023 quando a pasta canônica já existe no ano/cliente correto (ex.: 2025/Belliz/14796 - 025539-01 - ...).

Depois disso, a pipeline principal (segunda 05:00) mantém a estrutura de novas Features, anexos e Closed.

---

## 5. Metadados (colunas) nas pastas do SharePoint

É possível exibir colunas automáticas nas pastas (ex.: **Feature ID | Nº de Proposta | Título | Criado Em | Criado Por**) usando os metadados do item de lista (listItem) da pasta no SharePoint.

Para isso seria necessário:

1. **No SharePoint:** Criar as colunas na biblioteca e anotar os **nomes internos** de cada coluna.
2. **No código:** Ao criar ou garantir a pasta, atualizar o **listItem** da pasta via Graph (`PATCH .../listItem/fields`) com os valores do Azure DevOps.
3. **Dados do Azure DevOps:** Incluir **System.CreatedDate** (data completa) e **System.CreatedBy** (Criado Por) na varredura, além dos campos já usados (Feature ID, Nº Proposta, Título).

Implementação pode ser feita em uma etapa futura.
