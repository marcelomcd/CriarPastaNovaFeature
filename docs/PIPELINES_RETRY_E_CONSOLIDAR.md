# Pipeline principal e estrutura de pastas

**No Azure Repos há apenas uma pipeline:** a **pipeline principal** (`azure-pipelines.yml`). Para configurá-la, siga **[CONFIGURAR_PIPELINE.md](CONFIGURAR_PIPELINE.md)**.

---

## 1. Pipeline principal (azure-pipelines.yml)

- Varre as Features no Azure DevOps e, para cada uma, garante pasta no SharePoint, link no work item e sincronização de anexos.
- **Segundo passo automático:** Se alguma Feature falhar (ex.: 400 por campos obrigatórios vazios), a pipeline reprocessa **só esses itens** em um segundo passo: cria a pasta e sincroniza os anexos **sem** atualizar o campo no work item (evita novo 400). Assim, mesmo itens com erro de validação passam a ter pasta e anexos no SharePoint.
- **Agendamento:** semanal (domingos 5:00 BRT). Após a varredura completa inicial, cada execução processa só: novas Features, novos anexos e movimentação de pastas para **Closed** quando a Feature passa para Status Closed.

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

## 3. Consolidação de pastas (execução local)

A **consolidação** (unificar as pastas de origem em **Projetos DevOps**) não tem pipeline no Azure; é feita **localmente** quando você precisar.

1. No **`backend/.env`**, adicione:
   - **`SHAREPOINT_SOURCE_FOLDER_PATHS`** = `Documentação dos Clientes;Documentação dos Projetos;Projetos DevOps OLD;TestePowerAutomate`
2. Execute o **`run_pipelines_local.bat`** na raiz do projeto e escolha **2 (Consolidar)** ou **3 (Ambos)** — a opção 3 roda primeiro a varredura e depois a consolidação.

O script **`backend/pipeline_consolidate_sharepoint.py`** é o mesmo que rodava na antiga pipeline Consolidar; agora é chamado pelo .bat ou manualmente (`cd backend` e `python pipeline_consolidate_sharepoint.py`).

---

## 4. Metadados (colunas) nas pastas do SharePoint

É possível exibir colunas automáticas nas pastas (ex.: **Feature ID | Nº de Proposta | Título | Criado Em | Criado Por**) usando os metadados do item de lista (listItem) da pasta no SharePoint.

Para isso seria necessário:

1. **No SharePoint:** Criar as colunas na biblioteca e anotar os **nomes internos** de cada coluna.
2. **No código:** Ao criar ou garantir a pasta, atualizar o **listItem** da pasta via Graph (`PATCH .../listItem/fields`) com os valores do Azure DevOps.
3. **Dados do Azure DevOps:** Incluir **System.CreatedDate** (data completa) e **System.CreatedBy** (Criado Por) na varredura, além dos campos já usados (Feature ID, Nº Proposta, Título).

Implementação pode ser feita em uma etapa futura.
