# Pipeline "Consolidar SharePoint" e estrutura de pastas

Há **duas pipelines**: a **principal** (varredura Azure DevOps + SharePoint) e a **Consolidar SharePoint** (unificar documentos de várias pastas em uma só).

---

## 1. Pipeline principal (azure-pipelines.yml)

- Varre as Features no Azure DevOps e, para cada uma, garante pasta no SharePoint, link no work item e sincronização de anexos.
- **Segundo passo automático:** Se alguma Feature falhar (ex.: 400 por campos obrigatórios vazios), a pipeline reprocessa **só esses itens** em um segundo passo: cria a pasta e sincroniza os anexos **sem** atualizar o campo no work item (evita novo 400). Assim, mesmo itens com erro de validação passam a ter pasta e anexos no SharePoint.

---

## 2. Pipeline "Consolidar SharePoint" (azure-pipelines-consolidate.yml)

**Arquivo:** `azure-pipelines-consolidate.yml`

**Objetivo:** Mover todos os documentos de uma ou mais pastas do SharePoint (URLs de compartilhamento) para a pasta do projeto, usando **o mesmo padrão de estrutura** e **sem duplicar** arquivos.

**Estrutura de destino (igual à principal):**

- **Documentações de Projetos** > **Projetos DevOps** > **Ano** > **Cliente** > **Feature ID - Número de Proposta - Título**

A estrutura das pastas de origem é preservada: se na origem existir `Ano/Cliente/Feature.../arquivo.pdf`, o arquivo será colocado em `Projetos DevOps/Ano/Cliente/Feature.../arquivo.pdf`. Não se usa prefixo em arquivos; se o arquivo já existir na pasta de destino, é ignorado (não duplica).

### Como usar

1. Crie uma **nova pipeline** no Azure DevOps apontando para `azure-pipelines-consolidate.yml`.
2. Configure as variáveis (mesmas do SharePoint da pipeline principal + **`SHAREPOINT_SOURCE_FOLDER_URLS`**).
3. Defina **`SHAREPOINT_FOLDER_PATH_BASE=Projetos DevOps`** para que o destino seja **Documentações de Projetos > Projetos DevOps** (e abaixo as subpastas Ano > Cliente > Feature...).
4. Em **`SHAREPOINT_SOURCE_FOLDER_URLS`**, informe as URLs de compartilhamento das pastas de origem, separadas por **ponto e vírgula (;)**.  
   Exemplo:  
   `https://qualiitcombr.sharepoint.com/:f:/s/projetosqualiit/IgCYjhnxm56qQZsITxYIqeiPAWPNl2N3jEKbF_VatJxTc3Y?e=de9hzu;https://qualiitcombr.sharepoint.com/:f:/s/projetosqualiit/IgB9SwRtzkL1SocBGfXxmAMNAcrZURe5GIe4qMIIODpuWPw?e=DbWxCY`
5. Execute a pipeline. Os arquivos serão copiados mantendo a estrutura; arquivos que já existirem no destino serão ignorados.

### Variáveis obrigatórias (Consolidar)

| Variável | Descrição | Secreto? |
|----------|-----------|----------|
| `SHAREPOINT_CLIENT_ID` | Client ID do app (Entra ID) | Não |
| `SHAREPOINT_CLIENT_SECRET` | Client Secret | **Sim** |
| `SHAREPOINT_TENANT_ID` | Tenant ID | Não |
| `SHAREPOINT_SITE_URL` | URL do site SharePoint de destino | Não |
| `SHAREPOINT_FOLDER_PATH_BASE` | Pasta base de destino: **Projetos DevOps** | Não |
| **`SHAREPOINT_SOURCE_FOLDER_URLS`** | URLs de compartilhamento das pastas de origem, separadas por **;** | Não |

---

## 3. Estrutura de pastas no SharePoint

Padrão desejado:

- **Documentações de Projetos** > **Projetos DevOps** > **Ano** > **Cliente** > **Feature ID - Nº Proposta - Título**
- Para Features encerradas: **Documentações de Projetos** > **Projetos DevOps** > **Ano** > **Closed** > **Cliente** > **Feature ID - Nº Proposta - Título**

Configure **`SHAREPOINT_FOLDER_PATH_BASE=Projetos DevOps`** na pipeline (e no `.env`, se usar) para que a raiz seja **Projetos DevOps** (sem a camada "Documentos Compartilhados").

---

## 4. Metadados (colunas) nas pastas do SharePoint

É possível exibir colunas automáticas nas pastas (ex.: **Feature ID | Nº de Proposta | Título | Criado Em | Criado Por**) usando os metadados do item de lista (listItem) da pasta no SharePoint.

Para isso seria necessário:

1. **No SharePoint:** Criar as colunas na biblioteca e anotar os **nomes internos** de cada coluna.
2. **No código:** Ao criar ou garantir a pasta, atualizar o **listItem** da pasta via Graph (`PATCH .../listItem/fields`) com os valores do Azure DevOps.
3. **Dados do Azure DevOps:** Incluir **System.CreatedDate** (data completa) e **System.CreatedBy** (Criado Por) na varredura, além dos campos já usados (Feature ID, Nº Proposta, Título).

Implementação pode ser feita em uma etapa futura.
