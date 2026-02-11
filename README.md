<div align="center">

# FluxoNovasFeatures

### Integração Azure DevOps e SharePoint – pastas e documentação por Feature

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Azure DevOps](https://img.shields.io/badge/Azure%20DevOps-Integração-0078D7?style=for-the-badge&logo=azure-devops&logoColor=white)](https://dev.azure.com/)
[![SharePoint](https://img.shields.io/badge/SharePoint-Microsoft%20Graph-0078D4?style=for-the-badge&logo=microsoft-sharepoint&logoColor=white)](https://www.microsoft.com/sharepoint)
[![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)](LICENSE)

**Criação automática de pastas no SharePoint por Feature, preenchimento de `Custom.LinkPastaDocumentacao` e sincronização de anexos**

*Tempo real (webhooks) e varredura semanal (pipeline no Azure Repos)*

[Visão Geral](#visao-geral) • [Instalação](#instalacao-rapida) • [Configuração](#configuracao) • [Pipelines](#pipeline-e-service-hooks) • [Testes](#testes) • [API](#api-endpoints)

</div>

---

## Índice

- [Visão Geral](#visao-geral)
- [Funcionalidades](#funcionalidades)
- [Estrutura de pastas no SharePoint](#estrutura-de-pastas-no-sharepoint)
- [Arquitetura](#arquitetura)
- [Tecnologias](#tecnologias)
- [Pré-requisitos](#pre-requisitos)
- [Instalação Rápida](#instalacao-rapida)
- [Configuração](#configuracao)
- [Uso](#uso)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Testes](#testes)
- [API Endpoints](#api-endpoints)
- [Pipeline e Service Hooks](#pipeline-e-service-hooks)
- [Solução de Problemas](#solucao-de-problemas)
- [Referências](#referencias)
- [Licença](#licenca)

---

<a id="visao-geral"></a>
## Visão Geral

O **FluxoNovasFeatures** integra **Azure DevOps** e **SharePoint**: a cada nova Feature (ou atualização com anexos), o sistema cria a estrutura de pastas no SharePoint, preenche o campo customizado `Custom.LinkPastaDocumentacao` no work item e sincroniza os anexos da Feature para a pasta.

### Características principais

- **Tempo real**: Service Hooks do Azure DevOps disparam a API ao criar/atualizar work items (Feature).
- **Pipeline no Azure Repos** (`azure-pipelines.yml`): varredura de Features, criação de pastas no SharePoint, link no work item e sincronização de anexos. Agendada **semanalmente** (domingos 5:00 BRT); após a varredura completa inicial, processa só novas Features, novos anexos e movimentação para Closed.
- **Estrutura padronizada**: `{Base}/{Ano}/{Cliente}/{FeatureId} - {NumeroProposta} - {Título}`.
- **Segurança**: autenticação Microsoft Entra ID (MSAL) para SharePoint; PAT para Azure DevOps; validação de secret no webhook.

---

<a id="funcionalidades"></a>
## Funcionalidades

### Criação de pastas

- Criação em cadeia da pasta base e subpastas (Ano → Cliente → Pasta da Feature).
- Nome do cliente normalizado (title case) a partir do Area Path.
- Nome da pasta da Feature: `{Id} - {NumeroProposta} - {Título}` (sanitizado).

### Link de documentação

- Geração de link de compartilhamento (view, organization) no SharePoint.
- Atualização do campo `Custom.LinkPastaDocumentacao` no work item da Feature.

### Anexos

- Listagem de anexos da Feature via API Azure DevOps.
- Download e upload para a pasta da Feature no SharePoint (overwrite quando aplicável).

### API e varredura

- **POST /webhook/devops**: recebe eventos do Service Hook (work item created/updated).
- **GET /health**: health check da API.
- **POST /sync/feature/{feature_id}**: sincronização manual de uma Feature.
- Script `pipeline_feature_folders.py`: ponto de entrada da varredura (usado pela pipeline YAML).

---

<a id="estrutura-de-pastas-no-sharepoint"></a>
## Estrutura de pastas no SharePoint

```
{Base} / {Ano} / {Cliente} / {FeatureId} - {NumeroProposta} - {Título}
```

- **Base**: configurável (`SHAREPOINT_FOLDER_PATH_BASE`), ex.: `Documentos Compartilhados/Projetos DevOps`
- **Ano**: ano de criação da Feature
- **Cliente**: último segmento do Area Path, normalizado (ex.: CAMIL ALIMENTOS → Camil Alimentos)
- **FeatureId**, **NumeroProposta**, **Título**: da Feature no Azure DevOps

---

<a id="arquitetura"></a>
## Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│  Azure DevOps (Service Hooks)  →  POST /webhook/devops       │
│  Pipeline (agendada)            →  pipeline_feature_folders  │
├─────────────────────────────────────────────────────────────┤
│  FastAPI (main.py)                                          │
│  • Validação webhook / sync manual                           │
│  • FeatureFolderService (orquestração)                       │
├─────────────────────────────────────────────────────────────┤
│  AzureDevOpsClient          │  SharePointFileService        │
│  • list_features, get_wi    │  • ensure_folder_path         │
│  • update_work_item_link    │  • create_sharing_link         │
│  • list_attachment_relations│  • upload_file                 │
│  • download_attachment      │  (auth: SharePointAuthService)│
└─────────────────────────────────────────────────────────────┘
```

---

<a id="tecnologias"></a>
## Tecnologias

| Tecnologia | Propósito |
|------------|-----------|
| **Python** | 3.10+ |
| **FastAPI** | API HTTP (webhook, health, sync) |
| **Pydantic / pydantic-settings** | Configuração e validação |
| **MSAL** | Autenticação Microsoft Entra ID (SharePoint/Graph) |
| **requests** | Cliente HTTP (Azure DevOps, Microsoft Graph) |

---

<a id="pre-requisitos"></a>
## Pré-requisitos

- **Python 3.10+**
- **Conta Azure DevOps**: PAT com escopo Work Items (leitura e escrita para atualizar `Custom.LinkPastaDocumentacao`)
- **Microsoft Entra ID**: aplicativo com permissões SharePoint/Graph (ex.: Sites.ReadWrite.All)
- **Site SharePoint**: URL do site (ex.: `https://qualiitcombr.sharepoint.com/sites/projetosqualiit`)

---

<a id="instalacao-rapida"></a>
## Instalação Rápida

### 1. Clone o repositório

```bash
git clone https://dev.azure.com/qualiit/ALM/_git/Qualiit.FluxoNovasFeatures
cd Qualiit.FluxoNovasFeatures
```

### 2. Ambiente Python (backend)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```

### 3. Configuração

Copie `backend/.env.example` para `backend/.env` e preencha as variáveis (ver [Configuração](#configuracao)).

### 4. Executar a API

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- Health: `GET http://localhost:8000/health`
- Sync manual: `POST http://localhost:8000/sync/feature/{id}`

---

<a id="configuracao"></a>
## Configuração

Crie o arquivo `backend/.env` (nunca commite; está no `.gitignore`). Use como base o **`backend/.env.example`**, que contém todas as variáveis necessárias para a **Pipeline principal** e para a **Pipeline Consolidar**. Os mesmos nomes devem ser usados ao configurar as variáveis no Azure DevOps (Pipelines → Variables).

### Variáveis principais

| Variável | Descrição | Secreto? |
|----------|-----------|----------|
| `AZURE_DEVOPS_PAT` | Personal Access Token do Azure DevOps | Sim |
| `AZURE_DEVOPS_ORG` | Organização (ex.: qualiit) | Não |
| `AZURE_DEVOPS_PROJECT` | Nome do projeto | Não |
| `SHAREPOINT_CLIENT_ID` | Client ID do app no Entra ID | Não |
| `SHAREPOINT_CLIENT_SECRET` | Client Secret | Sim |
| `SHAREPOINT_TENANT_ID` | Tenant ID do Entra ID | Não |
| `SHAREPOINT_SITE_URL` | URL do site SharePoint | Não |
| `SHAREPOINT_FOLDER_PATH_BASE` | Pasta base: **Projetos DevOps** (não incluir nome da biblioteca) | Não |
| `WEBHOOK_SECRET` | Secret para validar Service Hooks | Sim (recomendado) |

Ver **`backend/.env.example`** e **[docs/CONFIGURAR_PIPELINE.md](docs/CONFIGURAR_PIPELINE.md)** para instruções completas de configuração da pipeline.

### Azure DevOps PAT

1. Azure DevOps → **User settings** → **Personal access tokens** → **New Token**
2. Escopo: **Work Items** (Read & write) para atualizar `Custom.LinkPastaDocumentacao`
3. Copie o token para `AZURE_DEVOPS_PAT` no `.env`

### SharePoint (Entra ID)

1. Registre um aplicativo no **Microsoft Entra ID** (Azure Portal)
2. Permissões: Microsoft Graph → **Sites.ReadWrite.All** (ou escopo equivalente para SharePoint)
3. Crie um **Client secret** e preencha `SHAREPOINT_CLIENT_ID`, `SHAREPOINT_CLIENT_SECRET`, `SHAREPOINT_TENANT_ID`
4. `SHAREPOINT_SITE_URL`: URL do site SharePoint onde as pastas serão criadas

---

<a id="uso"></a>
## Uso

### API (webhook + health + sync manual)

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- **Health**: `GET http://localhost:8000/health`
- **Sync manual**: `POST http://localhost:8000/sync/feature/12345` (substitua pelo ID da Feature)

### Varredura (script)

```bash
cd backend
python pipeline_feature_folders.py
```

Lista todas as Features (Area Path configurado), garante pasta + link + anexos para cada uma.

### Pipeline no Azure DevOps

- **Pipeline** (`azure-pipelines.yml`): varredura de Features, pastas no SharePoint, link e anexos. Agendamento **semanal** (domingos 5:00 BRT) e/ou disparo manual.

**Instruções completas** (criar pipeline, variáveis, executar): **[docs/CONFIGURAR_PIPELINE.md](docs/CONFIGURAR_PIPELINE.md)**. Estrutura de pastas: [docs/PIPELINES_RETRY_E_CONSOLIDAR.md](docs/PIPELINES_RETRY_E_CONSOLIDAR.md).

---

<a id="estrutura-do-projeto"></a>
## Estrutura do Projeto

```
Qualiit.FluxoNovasFeatures/
├── backend/
│   ├── app/
│   │   ├── config.py              # Configurações (Pydantic Settings)
│   │   ├── models/                 # feature_folder, devops_models
│   │   ├── services/               # devops_client, sharepoint_auth, sharepoint_files, feature_folder_service
│   │   └── utils/                  # name_utils (normalização, sanitização)
│   ├── tests/                      # Testes unitários e de integração
│   ├── main.py                     # FastAPI: webhook, health, sync
│   ├── pipeline_feature_folders.py # Entrada da varredura
│   ├── requirements.txt
│   ├── .env.example
│   └── pytest.ini
├── docs/
│   ├── CONFIGURAR_PIPELINE.md      # Instruções para configurar a pipeline
│   └── PIPELINES_RETRY_E_CONSOLIDAR.md  # Estrutura de pastas e retry/erros
├── azure-pipelines.yml             # Pipeline (varredura semanal)
├── README.md
└── README_DE_EXEMPLO.md
```

---

<a id="testes"></a>
## Testes

### Testes unitários (não exigem .env)

```bash
cd backend
pip install -r requirements.txt
python -m pytest tests/ -v -m "not integration"
```

Cobre: `name_utils`, modelos `feature_folder`, `feature_folder_service` (conversões e datas), health da API.

### Testes de integração (exigem .env preenchido)

Validam **leitura/escrita no SharePoint** (criar pasta, upload, link) e **leitura no Azure DevOps** (listar Features, obter work item, listar anexos). Não alteram dados reais além de uma pasta de teste no SharePoint.

```bash
cd backend
# Garanta que .env está preenchido (SharePoint e Azure DevOps)
python -m pytest tests/ -v -m integration
```

Se as variáveis não estiverem configuradas, os testes de integração são **ignorados** (skipped).

### Todos os testes

```bash
cd backend
python -m pytest tests/ -v
```

---

<a id="api-endpoints"></a>
## API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/health` | Health check (status da API) |
| `POST` | `/webhook/devops` | Recebe Service Hook (work item created/updated); valida `X-Webhook-Secret` |
| `POST` | `/sync/feature/{feature_id}` | Sincronização manual: pasta + link + anexos para a Feature |

---

<a id="pipeline-e-service-hooks"></a>
## Pipeline e Service Hooks

- **Pipeline**: **Instruções passo a passo** (criar, variáveis, executar) em **[docs/CONFIGURAR_PIPELINE.md](docs/CONFIGURAR_PIPELINE.md)**. Agendamento semanal (domingos 5:00 BRT) e disparo manual. Estrutura de pastas e retry: [PIPELINES_RETRY_E_CONSOLIDAR.md](docs/PIPELINES_RETRY_E_CONSOLIDAR.md).
- **Service Hooks (tempo real)**: **Project Settings** → **Service hooks** → **Create subscription** — eventos **Work item created** e **Work item updated**, URL `https://<sua-api>/webhook/devops`, header `X-Webhook-Secret` = valor de `WEBHOOK_SECRET`.

---

<a id="solucao-de-problemas"></a>
## Solução de Problemas

### Erro de autenticação Azure DevOps

- Verifique `AZURE_DEVOPS_PAT` (não expirado, escopo Work Items).
- Confirme `AZURE_DEVOPS_ORG` e `AZURE_DEVOPS_PROJECT`.

### Erro ao acessar SharePoint

- Confirme `SHAREPOINT_SITE_URL`, `SHAREPOINT_CLIENT_ID`, `SHAREPOINT_CLIENT_SECRET`, `SHAREPOINT_TENANT_ID`.
- Verifique permissões do app no Entra ID (Sites.ReadWrite.All ou equivalente).

### Webhook retorna 401

- Configure `WEBHOOK_SECRET` no `.env` e o mesmo valor no header `X-Webhook-Secret` da subscription no Azure DevOps.

### Testes de integração não rodam

- Preencha o `backend/.env` com credenciais válidas; os testes de integração são skipped quando as variáveis estão vazias ou placeholder.

---

<a id="referencias"></a>
## Referências

- [Azure DevOps - Attachments](https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/attachments/get?view=azure-devops-rest-7.1)
- [Microsoft Graph - Create sharing link](https://learn.microsoft.com/en-us/graph/api/driveitem-createlink?view=graph-rest-1.0)
- [FastAPI](https://fastapi.tiangolo.com/)

---

<a id="licenca"></a>
## Licença

Este projeto é **proprietário** da **Quali IT - Inovação e Tecnologia**. Todos os direitos reservados.

---

<div align="center">

**Repositório**: [Qualiit.FluxoNovasFeatures](https://dev.azure.com/qualiit/ALM/_git/Qualiit.FluxoNovasFeatures)

---

**Última atualização**: 10/02/2026  
**Versão**: 1.0.0  
**Backend**: Python / FastAPI  
**Desenvolvido por**: Marcelo Macedo  
**E-mail**: [marcelo.macedo@qualiit.com.br](mailto:marcelo.macedo@qualiit.com.br)

</div>
