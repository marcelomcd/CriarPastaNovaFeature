# Pipeline "Consolidar SharePoint" e estrutura de pastas

**Para configurar variáveis e criar as duas pipelines no Azure DevOps**, siga **[CONFIGURAR_PIPELINE.md](CONFIGURAR_PIPELINE.md)**.

Há **duas pipelines**: a **principal** (varredura Azure DevOps + SharePoint) e a **Consolidar SharePoint** (unificar documentos de várias pastas em uma só).

---

## 1. Pipeline principal (azure-pipelines.yml)

- Varre as Features no Azure DevOps e, para cada uma, garante pasta no SharePoint, link no work item e sincronização de anexos.
- **Segundo passo automático:** Se alguma Feature falhar (ex.: 400 por campos obrigatórios vazios), a pipeline reprocessa **só esses itens** em um segundo passo: cria a pasta e sincroniza os anexos **sem** atualizar o campo no work item (evita novo 400). Assim, mesmo itens com erro de validação passam a ter pasta e anexos no SharePoint.

---

## 2. Pipeline "Consolidar SharePoint" (azure-pipelines-consolidate.yml)

**Arquivo:** `azure-pipelines-consolidate.yml`

**Objetivo:** Obter e mover **todas** as pastas e arquivos de **quatro pastas de origem** (na mesma biblioteca do site) para a pasta **Projetos DevOps**, mantendo a estrutura **Ano > Cliente > Feature ID - Nº Proposta - Título**. A estrutura é unificada com base no **Feature ID**, evitando pastas duplicadas ou do mesmo projeto com nomes parecidos. Arquivos que já existirem no destino são ignorados.

### Pastas de origem (4) e destino

| Tipo | Pasta (caminho na biblioteca) | Link (AllItems) |
|------|-------------------------------|------------------|
| Origem | Documentação dos Clientes | [Abrir](https://qualiitcombr.sharepoint.com/sites/projetosqualiit/Documentos%20Compartilhados/Forms/AllItems.aspx?id=%2Fsites%2Fprojetosqualiit%2FDocumentos%20Compartilhados%2FDocumenta%C3%A7%C3%A3o%20dos%20Clientes) |
| Origem | Documentação dos Projetos | [Abrir](https://qualiitcombr.sharepoint.com/sites/projetosqualiit/Documentos%20Compartilhados/Forms/AllItems.aspx?id=%2Fsites%2Fprojetosqualiit%2FDocumentos%20Compartilhados%2FDocumenta%C3%A7%C3%A3o%20dos%20Projetos) |
| Origem | Projetos DevOps OLD | [Abrir](https://qualiitcombr.sharepoint.com/sites/projetosqualiit/Documentos%20Compartilhados/Forms/AllItems.aspx?id=%2Fsites%2Fprojetosqualiit%2FDocumentos%20Compartilhados%2FProjetos%20DevOps%20OLD) |
| Origem | TestePowerAutomate | [Abrir](https://qualiitcombr.sharepoint.com/sites/projetosqualiit/Documentos%20Compartilhados/Forms/AllItems.aspx?id=%2Fsites%2Fprojetosqualiit%2FDocumentos%20Compartilhados%2FTestePowerAutomate) |
| **Destino** | **Projetos DevOps** | [Abrir](https://qualiitcombr.sharepoint.com/sites/projetosqualiit/Documentos%20Compartilhados/Forms/AllItems.aspx?id=%2Fsites%2Fprojetosqualiit%2FDocumentos%20Compartilhados%2FProjetos%20DevOps) |

**Estrutura de destino (igual à principal):** Documentações de Projetos > **Projetos DevOps** > **Ano** > **Cliente** > **Feature ID - Número de Proposta - Título**. A estrutura relativa das origens é preservada; pastas e arquivos são reunidos por Feature ID (evita duplicidade de pastas do mesmo projeto).

### Como usar

1. Crie uma **nova pipeline** no Azure DevOps apontando para `azure-pipelines-consolidate.yml`.
2. Configure as variáveis (mesmas do SharePoint da pipeline principal) e **uma** das duas opções de origem:
   - **Recomendado — por caminho:** `SHAREPOINT_SOURCE_FOLDER_PATHS` com os nomes das pastas na biblioteca, separados por **;**  
     Exemplo: `Documentação dos Clientes;Documentação dos Projetos;Projetos DevOps OLD;TestePowerAutomate`
   - **Por link de compartilhamento:** `SHAREPOINT_SOURCE_FOLDER_URLS` com as URLs `/:f:/s/...?e=xxx` separadas por **;**.
3. Defina **`SHAREPOINT_FOLDER_PATH_BASE=Projetos DevOps`** (apenas o nome da pasta; a API já usa a biblioteca como raiz).
4. Execute a pipeline. Os arquivos serão copiados mantendo a estrutura; arquivos já existentes no destino são ignorados.

### Variáveis obrigatórias (Consolidar)

| Variável | Descrição | Secreto? |
|----------|-----------|----------|
| `SHAREPOINT_CLIENT_ID` | Client ID do app (Entra ID) | Não |
| `SHAREPOINT_CLIENT_SECRET` | Client Secret | **Sim** |
| `SHAREPOINT_TENANT_ID` | Tenant ID | Não |
| `SHAREPOINT_SITE_URL` | URL do site SharePoint | Não |
| `SHAREPOINT_FOLDER_PATH_BASE` | Apenas **Projetos DevOps** (não incluir nome da biblioteca) | Não |
| **`SHAREPOINT_SOURCE_FOLDER_PATHS`** ou **`SHAREPOINT_SOURCE_FOLDER_URLS`** | Caminhos na biblioteca (ex.: `Documentação dos Clientes;Projetos DevOps OLD`) **ou** URLs de compartilhamento das pastas de origem, separados por **;** | Não |

**No Azure DevOps:** Pipelines → sua pipeline Consolidar → **Variables**. Para as 4 pastas acima, use **`SHAREPOINT_SOURCE_FOLDER_PATHS`** com:  
`Documentação dos Clientes;Documentação dos Projetos;Projetos DevOps OLD;TestePowerAutomate`

**Para rodar o script localmente** (`python backend/pipeline_consolidate_sharepoint.py`): no `.env`, além das variáveis de SharePoint, defina `SHAREPOINT_SOURCE_FOLDER_PATHS` ou `SHAREPOINT_SOURCE_FOLDER_URLS`. Veja `backend/.env.example`.

---

## 3. Estrutura de pastas no SharePoint

**Pasta base do projeto (subpasta):** **Projetos DevOps**  
Ela fica em Documentos Compartilhados. Dentro dela a pipeline cria as subpastas **Ano** > **Cliente** (ou **Closed**) > **Feature ID - Nº Proposta - Título**.

- [Abrir pasta Projetos DevOps](https://qualiitcombr.sharepoint.com/sites/projetosqualiit/Documentos%20Compartilhados/Forms/AllItems.aspx?id=%2Fsites%2Fprojetosqualiit%2FDocumentos%20Compartilhados%2FProjetos%20DevOps)

**Estrutura criada dentro de Projetos DevOps:**

- **Ano** (ex.: 2025) > **Cliente** > **Feature ID - Nº Proposta - Título** (Features ativas)
- **Ano** > **Closed** > **Cliente** > **Feature ID - Nº Proposta - Título** (Features encerradas)

Configure **`SHAREPOINT_FOLDER_PATH_BASE=Projetos DevOps`** na pipeline e no `.env`. Não use o nome da biblioteca (Documentações de Projetos) para evitar criar a pasta em duplicidade.

---

## 4. Metadados (colunas) nas pastas do SharePoint

É possível exibir colunas automáticas nas pastas (ex.: **Feature ID | Nº de Proposta | Título | Criado Em | Criado Por**) usando os metadados do item de lista (listItem) da pasta no SharePoint.

Para isso seria necessário:

1. **No SharePoint:** Criar as colunas na biblioteca e anotar os **nomes internos** de cada coluna.
2. **No código:** Ao criar ou garantir a pasta, atualizar o **listItem** da pasta via Graph (`PATCH .../listItem/fields`) com os valores do Azure DevOps.
3. **Dados do Azure DevOps:** Incluir **System.CreatedDate** (data completa) e **System.CreatedBy** (Criado Por) na varredura, além dos campos já usados (Feature ID, Nº Proposta, Título).

Implementação pode ser feita em uma etapa futura.
