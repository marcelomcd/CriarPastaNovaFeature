<div align="center">

# 🚦 NewFarol

### Sistema de Gestão de Projetos Azure DevOps

[![Node.js](https://img.shields.io/badge/Node.js-18+-339933?style=for-the-badge&logo=node.js&logoColor=white)](https://nodejs.org/)
[![Express](https://img.shields.io/badge/Express-4.18+-000000?style=for-the-badge&logo=express&logoColor=white)](https://expressjs.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)](LICENSE)

**Plataforma profissional para visualização e gestão de projetos do Azure DevOps**

*Construído com arquitetura modular e boas práticas de engenharia de software*

[Documentação](#documentacao) • [Instalação](#instalacao-rapida) • [Configuração](#configuracao) • [API](#api-endpoints) • [Git Submodules](#git-submodules)

</div>

---

## 📑 Índice

- [Visão Geral](#visao-geral)
- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Tecnologias](#tecnologias)
- [Pré-requisitos](#pre-requisitos)
- [Instalação Rápida](#instalacao-rapida)
- [Configuração](#configuracao)
- [Uso](#uso)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [API Endpoints](#api-endpoints)
- [Integração com Azure DevOps](#integracao-com-azure-devops)
- [Autenticação](#autenticacao)
- [Sistema Unificado](#sistema-unificado)
- [Git Submodules](#git-submodules)
- [Desenvolvimento](#desenvolvimento)
- [Solução de Problemas](#solucao-de-problemas)
- [Deploy](#deploy)
- [Documentação](#documentacao)
- [Histórico de versões](#historico-de-versoes)
- [Contribuindo](#contribuindo)
- [Licença](#licenca)

---

<a id="visao-geral"></a>
## 🎯 Visão Geral

O **NewFarol** é uma plataforma completa e moderna para visualização e gestão de projetos do Azure DevOps, desenvolvida pela **Quali IT - Inovação e Tecnologia**. O sistema oferece uma interface intuitiva e poderosa para acompanhar métricas, gerenciar projetos e tomar decisões baseadas em dados em tempo real.

### 🎨 Características Principais

- **Dashboard Interativo** com visualizações em tempo real
- **Arquitetura Modular** com separação clara de responsabilidades
- **Performance Otimizada** com cache inteligente e WIQL
- **Interface Moderna** com glassmorphism e tema claro/escuro
- **Segurança Robusta** com autenticação OAuth 2.0
- **Integração Completa** com Azure DevOps via WIQL
- **Sistema Unificado** integrando New Farol e Painel Service UP

---

<a id="funcionalidades"></a>
## ✨ Funcionalidades

### 📊 Dashboard Interativo

- **Métricas em Tempo Real**: Visualização instantânea de projetos, status e faróis
- **Gráficos Dinâmicos**: Análise visual de dados com Recharts
- **Filtros Avançados**: Por cliente, PMO, estado, farol e período
- **Exportação para Excel**: Relatórios completos em formato .xlsx
- **Modo Escuro/Claro**: Interface adaptável com glassmorphism

### 🔍 Gestão de Features

- **Listagem Completa**: Todas as features com filtros e busca
- **Detalhes Detalhados**: Informações completas de cada projeto
- **Sincronização Automática**: Atualização via WIQL direto do Azure DevOps
- **Validação Inteligente**: Clientes validados contra Epics

### 📈 Relatórios e Análises

- **Relatórios Personalizados**: Análises sob medida
- **Métricas de Performance**: KPIs e indicadores de projeto
- **Análise Temporal**: Tendências e histórico de fechamentos
- **Agrupamentos**: Por cliente, PMO, responsável e estado

### 🔐 Segurança e Acesso

- **Autenticação OAuth 2.0**: Integração com Azure AD
- **Controle de Acesso**: Baseado em domínio de e-mail
- **Rate Limiting**: Proteção contra abuso de API
- **Logs Estruturados**: Rastreabilidade completa

### 🎯 Sistema Unificado

- **New Farol**: Gestão de projetos Azure DevOps
- **Painel Service UP**: Gestão de chamados (sistema independente)
- **Integração via iframe**: Total independência entre sistemas
- **Isolamento Total**: Alterações em um sistema não afetam o outro

---

<a id="arquitetura"></a>
## 🏗️ Arquitetura

O projeto segue uma **arquitetura modular** com separação clara de responsabilidades, garantindo manutenibilidade, testabilidade e escalabilidade.

### Backend (Node.js + Express)

```
┌─────────────────────────────────────────────┐
│         API Layer (Routes)                   │  ← Endpoints HTTP REST
│  • Rotas Express                             │
│  • Middleware (CORS, Error Handling)        │
│  • Validação de Requisições                  │
├─────────────────────────────────────────────┤
│      Business Logic Layer                    │  ← Lógica de Negócio
│  • Processamento de Dados                   │
│  • Normalização e Transformação              │
│  • Cache com TTL                             │
├─────────────────────────────────────────────┤
│   Infrastructure Layer (Clients)             │  ← Integrações Externas
│  • Azure DevOps Client (WIQL)               │
│  • JWT Authentication                        │
│  • TTL Cache                                 │
└─────────────────────────────────────────────┘
```

**Princípios Aplicados:**
- ✅ **Separation of Concerns**: Cada camada tem responsabilidade única
- ✅ **Modular Design**: Módulos independentes e reutilizáveis
- ✅ **Single Responsibility**: Funções com uma única responsabilidade
- ✅ **DRY (Don't Repeat Yourself)**: Código reutilizável

### Frontend (React + TypeScript)

```
┌─────────────────────────────────────────────┐
│         Pages (Composição)                   │
│  • Páginas principais                        │
│  • Roteamento                                │
├─────────────────────────────────────────────┤
│      Components (UI Pura)                    │
│  • Componentes reutilizáveis                 │
│  • Presentational Components                 │
├─────────────────────────────────────────────┤
│    Hooks (Lógica Reutilizável)               │
│  • Custom Hooks                              │
│  • React Query Hooks                         │
├─────────────────────────────────────────────┤
│    Services (Comunicação API)                │
│  • API Clients                               │
│  • Type-safe Requests                        │
└─────────────────────────────────────────────┘
```

**Padrões Utilizados:**
- 🎯 **Component Composition**: Componentes pequenos e focados
- 🔄 **Custom Hooks**: Lógica reutilizável encapsulada
- 📡 **React Query**: Gerenciamento de estado servidor
- 🎨 **Tailwind CSS**: Utility-first styling

---

<a id="tecnologias"></a>
## 🛠️ Tecnologias

### Backend Stack

| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| **Node.js** | 18+ | Runtime JavaScript |
| **Express** | 4.18+ | Framework web |
| **Axios** | 1.6+ | Cliente HTTP para Azure DevOps |
| **jsonwebtoken** | 9.0+ | Autenticação JWT |
| **dotenv** | 16.3+ | Gerenciamento de variáveis de ambiente |
| **cors** | 2.8+ | Configuração CORS |

### Frontend Stack

| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| **React** | 18+ | Biblioteca UI |
| **TypeScript** | 5+ | Tipagem estática |
| **Vite** | 5+ | Build tool |
| **React Query** | 5.12+ | Estado servidor |
| **Tailwind CSS** | 3.3+ | Framework CSS |
| **Recharts** | 2.10+ | Gráficos |
| **Axios** | 1.6+ | HTTP client |
| **React Router** | 6.20+ | Roteamento |

### Ferramentas de Desenvolvimento

- **ESLint**: Linter JavaScript/TypeScript
- **Prettier**: Formatação de código (opcional)
- **Git**: Controle de versão

---

<a id="pre-requisitos"></a>
## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

### Obrigatórios

- ✅ **Node.js 18+** - [Download](https://nodejs.org/)
- ✅ **Git** - [Download](https://git-scm.com/)

### Opcionais (Produção)

- 🔐 **Conta Azure DevOps** com PAT (Personal Access Token)
- 🔑 **Aplicação Azure AD** configurada para OAuth

### Verificação Rápida

```bash
# Verificar Node.js
node --version    # Deve ser 18 ou superior

# Verificar npm
npm --version     # Deve ser 9 ou superior

# Verificar Git
git --version
```

---

<a id="instalacao-rapida"></a>
## ⚡ Instalação Rápida

### 1️⃣ Clone o Repositório

```bash
git clone https://dev.azure.com/qualiit/ALM/_git/Qualiit.Portal.Clients.v3
cd NewFarol
```

### 2️⃣ Instalação Automática (Recomendado)

Execute o script `start.bat` que instala todas as dependências automaticamente:

```bash
# Windows
start.bat
```

O script irá:
- ✅ Verificar se Node.js está instalado
- ✅ Instalar dependências do backend New Farol
- ✅ Instalar dependências do frontend New Farol
- ✅ Instalar dependências do backend ServiceUp
- ✅ Instalar dependências do frontend ServiceUp
- ✅ Criar arquivo `.env` com configurações padrão
- ✅ Iniciar todos os servidores

### 3️⃣ Instalação Manual

#### Backend New Farol

```bash
cd backend
npm install
```

#### Frontend New Farol

```bash
cd frontend
npm install
```

#### Backend ServiceUp (Opcional)

```bash
cd "Painel Service UP/backend"
npm install
```

#### Frontend ServiceUp (Opcional)

```bash
cd "Painel Service UP/frontend"
npm install
```

### 4️⃣ Configuração

Siga as instruções na seção [Configuração](#-configuracao) para configurar as variáveis de ambiente.

### 5️⃣ Executar

**Opção 1: Script Automático (Recomendado)**

```bash
start.bat
```

**Opção 2: Manual**

```bash
# Terminal 1 - Backend New Farol
cd backend
npm run dev

# Terminal 2 - Frontend New Farol
cd frontend
npm run dev

# Terminal 3 - Backend ServiceUp (Opcional)
cd "Painel Service UP/backend"
npm run dev

# Terminal 4 - Frontend ServiceUp (Opcional)
cd "Painel Service UP/frontend"
npm run dev
```

**Acesse:**
- 🚀 **New Farol**: http://localhost:5173
- 🚀 **ServiceUp Standalone**: http://localhost:5174
- 🚀 **ServiceUp via New Farol**: http://localhost:5173/serviceup

---

<a id="configuracao"></a>
## ⚙️ Configuração

<details>
<summary><strong>🔧 Backend New Farol - Variáveis de Ambiente</strong></summary>

Crie um arquivo `.env` na raiz do `backend`:

```env
# ============================================
# Azure DevOps Configuration
# ============================================
AZDO_PAT=seu-personal-access-token-aqui
AZDO_ORG=qualiit
AZDO_BASE_URL=https://dev.azure.com/qualiit/
AZDO_ROOT_PROJECT=Quali IT Inovacao e Tecnologia
AZDO_API_VERSION=7.0

# ============================================
# Server Configuration
# ============================================
PORT=8000
NODE_ENV=development

# ============================================
# Frontend Configuration
# ============================================
FRONTEND_URL=http://localhost:5173

# ============================================
# Azure AD OAuth Configuration
# ============================================
AZURE_AD_TENANT_ID=seu-tenant-id
AZURE_AD_CLIENT_ID=seu-client-id
AZURE_AD_CLIENT_SECRET=seu-client-secret
AZURE_AD_REDIRECT_URI=http://localhost:8000/api/auth/callback
AZURE_AD_IS_PUBLIC_CLIENT=true

# ============================================
# Security Configuration
# ============================================
SECRET_KEY=seu-secret-key-minimo-32-caracteres-aleatorios
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ============================================
# Application Configuration
# ============================================
APP_NAME=NewFarol
DEBUG=false
```

</details>

<details>
<summary><strong>⚛️ Frontend New Farol - Variáveis de Ambiente</strong></summary>

O frontend não requer arquivo `.env` separado. A configuração é feita via proxy no `vite.config.ts`:

```typescript
// vite.config.ts já configurado
server: {
  port: 5173,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

</details>

<details>
<summary><strong>🔧 Painel Service UP - Variáveis de Ambiente</strong></summary>

O Painel Service UP é um sistema independente que requer sua própria configuração.

1. **Local:** copie `Painel Service UP/backend/.env.example` para `Painel Service UP/backend/.env` e preencha (MySQL: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME=dw_combio`; API: `PORT`, `NODE_ENV`). O `.env` está no `.gitignore` e **nunca** deve ser commitado.

2. **Produção / Azure Repos:** configurar as mesmas variáveis como **Variable groups** (Pipelines) ou **Azure Key Vault** / secrets do App Service; o backend lê `process.env` normalmente.

Variáveis utilizadas: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `PORT`, `NODE_ENV`.

</details>

<details>
<summary><strong>🔐 Configuração do Azure AD</strong></summary>

#### Passo 1: Registrar Aplicação no Azure Portal

1. Acesse: [Azure Portal](https://portal.azure.com) > **Microsoft Entra ID** > **Registros de aplicativo**
2. Clique em **"Novo registro"** (ou edite o app **Farol Operacional**)
3. Configure:
   - **Name**: `NewFarol` / Farol Operacional
   - **Supported account types**: Use **"Contas somente neste diretório organizacional (apenas Quali IT)"**. Usuários de outras empresas (Consigaz, etc.) entram como **convidados B2B** no tenant Quali IT — veja passo 5 abaixo. (Se o app estiver como multitenant, altere de volta para único tenant.)

4. **Autenticação (Authentication)** — essencial para evitar erro `AADSTS700025`:
   - Vá em **Autenticação** no menu do app.
   - Em **Configurações de plataforma**, adicione uma plataforma **Web** (não apenas SPA):
     - Clique em **"Adicionar uma plataforma"** > **Web**
     - Em **URIs de redirecionamento**, adicione: `http://localhost:8000/api/auth/callback`
     - (Em produção, adicione também `https://seu-dominio/api/auth/callback`)
   - Em **Clientes públicos**, deixe **Permitir fluxos de cliente público** = **Não**.  
     Se estiver **Sim**, o Entra ID trata o app como cliente público e rejeita `client_secret` na troca do código por token (erro AADSTS700025).
   - Opcional: adicione plataforma **Single-page application (SPA)** com URI `http://localhost:5173/auth/success` para o frontend.

Resumo: o callback do backend (`/api/auth/callback`) deve ser **Web** e o app **não** pode ser “cliente público”.

#### Passo 2: Configurar Permissões (Farol Operacional / Entra ID)

Para o **login OAuth2** (Entrar com Microsoft) o Farol Operacional precisa apenas de **permissões delegadas**:

| Permissão     | Tipo      | Descrição                          | Necessária para login |
|---------------|-----------|------------------------------------|------------------------|
| **User.Read** | Delegado  | Sign in and read user profile      | ✅ Sim                 |
| **email**     | Delegado  | View users' email address          | ✅ Sim                 |
| **openid**    | Delegado  | Sign users in (OpenID Connect)      | ✅ Sim (já incluído com User.Read) |

**O que fazer no portal (Permissões de APIs):**

1. Vá em **Registros de aplicativo** > **Farol Operacional** > **Permissões de APIs**.
2. Confirme que existem **User.Read** e **email** (tipo **Delegado**). Adicione com **"+ Adicionar uma permissão"** > **Microsoft Graph** > **Permissões delegadas** se faltar.
3. **Remova** a permissão **User.Read.All** (tipo **Aplicativo**) se o app não precisar listar todos os usuários do diretório — ela não é usada no fluxo de login e costuma exibir "Não concedido para qualiit.com.br".
4. Clique em **"Conceder consentimento do administrador para qualiit.com.br"** para que **User.Read** e **email** fiquem com status concedido (evita falhas de consent no login).

Após conceder o consentimento, as colunas "Consentimento do administrador" e "Status" devem indicar que as permissões estão concedidas para o tenant.

#### Passo 3: Obter Credenciais

1. **Tenant ID**: Disponível na página **Overview**
2. **Client ID**: **Application (client) ID** na página Overview
3. **Client Secret**: 
   - Vá em **Certificates & secrets**
   - Clique em **"New client secret"**
   - Copie o valor (só aparece uma vez!)

#### Passo 4: Configurar no Backend

Adicione as credenciais no arquivo `.env` do backend:

```env
AZURE_AD_TENANT_ID=seu-tenant-id-aqui
AZURE_AD_CLIENT_ID=seu-client-id-aqui
AZURE_AD_CLIENT_SECRET=seu-client-secret-aqui
AZURE_AD_REDIRECT_URI=http://localhost:8000/api/auth/callback
# Use false para ativar login real com Microsoft Entra ID; true apenas para dev sem Azure
AZURE_AD_IS_PUBLIC_CLIENT=false
```

#### Passo 5: Convidar usuários de outras empresas (B2B) — sem aprovação do admin deles

O Farol é da **Quali IT**. Para que alguém de outra empresa (ex.: tecnologia@consigaz.com.br) faça login **sem** tela de "Aprovação necessária" no tenant da empresa dele:

1. No **tenant Quali IT**: [Azure Portal](https://portal.azure.com) > **Microsoft Entra ID** > **Usuários** > **Novo usuário convidado** (ou **Users** > **Invite external user**).
2. Informe o **e-mail** do usuário externo (ex.: `tecnologia@consigaz.com.br`), nome de exibição e mensagem de convite (opcional).
3. Clique em **Convidar**. O usuário recebe um e-mail; ao aceitar, passa a existir no diretório da Quali IT como **convidado**.
4. A partir daí ele acessa o Farol normalmente (Entrar com Microsoft), autenticando no **tenant Quali IT**. Nenhuma aprovação do admin da Consigaz é necessária.
5. O backend continua filtrando os dados pelo domínio do e-mail (`utils/auth.js`): usuário @consigaz.com.br vê apenas dados do cliente Consigaz.

Resumo: **app single-tenant (só Quali IT) + convidados B2B** = sistema é seu, você controla quem entra; a outra empresa não precisa aprovar app.

⚠️ **IMPORTANTE**: 
- Configure os Redirect URIs no Azure Portal conforme mostrado acima
- O Client Secret expira - configure um lembrete para renovar
- Para OAuth2 com Entra ID: defina `AZURE_AD_CLIENT_SECRET` e `AZURE_AD_IS_PUBLIC_CLIENT=false`
- Nunca commite o arquivo `.env` no Git (já está no `.gitignore`)

</details>

<details>
<summary><strong>🔑 Configuração do Azure DevOps PAT</strong></summary>

1. Acesse: [Azure DevOps](https://dev.azure.com/qualiit) > **User settings** > **Personal access tokens**
2. Clique em **"New Token"**
3. Configure:
   - **Name**: `NewFarol Access`
   - **Organization**: `qualiit`
   - **Expiration**: Escolha um período (ex: 90 dias)
   - **Scopes**: Selecione **Code (Read & write)** e **Work Items (Read)**
4. Clique em **"Create"** e copie o token
5. Adicione no `.env` do backend: `AZDO_PAT=seu-token-aqui`

⚠️ **Importante**: 
- O token só aparece uma vez - guarde-o com segurança
- Configure um lembrete para renovar antes de expirar
- Use tokens com escopo mínimo necessário

</details>

---

<a id="uso"></a>
## 🎮 Uso

### Acessar a Aplicação

1. **Execute o script de inicialização**:
   ```bash
   start.bat
   ```
   O script inicia automaticamente todos os servidores necessários.

2. **Acesse a aplicação**:
   - **New Farol**: http://localhost:5173
   - **ServiceUp Standalone**: http://localhost:5174
   - **ServiceUp via New Farol**: http://localhost:5173/serviceup

3. **Faça login** com sua conta Microsoft (OAuth)

4. **Explore o Dashboard** com métricas e visualizações

<details>
<summary><strong>📊 Funcionalidades Principais</strong></summary>

#### 📊 Dashboard

- **Cards de Métricas**: Total de projetos, em aberto, atrasados, próximos do prazo
- **Gráficos Interativos**: 
  - Distribuição por Status (Pizza)
  - Projetos por PMO (Barras)
  - Projetos por Responsável (Barras)
  - Features Fechadas por Dia (Linha)
- **Filtros Avançados**: Por cliente, PMO, estado, farol
- **Exportação**: Botão para exportar dados para Excel

#### 📋 Features

- **Listagem Completa**: Todas as features com paginação
- **Busca e Filtros**: Por estado, cliente, PMO, responsável
- **Detalhes**: Clique em uma feature para ver informações completas
- **Sincronização**: Dados atualizados via WIQL do Azure DevOps

#### 📈 Relatórios

- **Relatórios Personalizados**: Execute análises sob medida
- **Métricas de Performance**: KPIs e indicadores
- **Análises Temporais**: Tendências e histórico

#### 🎯 Painel Service UP

- **Gestão de Chamados**: Visualização e gestão de chamados
- **Dashboard de SLA**: Acompanhamento de SLA
- **Análises**: Relatórios e métricas de chamados
- **Integração Independente**: Sistema totalmente independente do New Farol

</details>

---

<a id="estrutura-do-projeto"></a>
## 📁 Estrutura do Projeto

```
NewFarol/
│
├── 📂 backend/                          # Backend Node.js/Express (New Farol)
│   ├── 📂 routes/                       # Rotas HTTP
│   │   ├── auth.js                     # Autenticação
│   │   ├── features.js                 # Features
│   │   ├── azdo.js                     # Endpoint consolidado
│   │   ├── workItems.js                # Work Items
│   │   ├── projects.js                 # Projetos
│   │   ├── reports.js                  # Relatórios
│   │   ├── export.js                   # Exportação
│   │   ├── webhooks.js                 # Webhooks
│   │   ├── clients.js                  # Clientes
│   │   ├── featuresAnalytics.js        # Analytics
│   │   └── featuresV2.js               # API v2
│   │
│   ├── 📂 utils/                        # Utilitários
│   │   ├── wiql.js                     # Queries WIQL
│   │   ├── wiqlClient.js               # Cliente WIQL
│   │   ├── normalization.js            # Normalização de dados
│   │   ├── ttlCache.js                 # Cache TTL
│   │   ├── azureDevOpsClientExtended.js # Cliente Azure DevOps
│   │   └── auth.js                     # Utilitários de autenticação
│   │
│   ├── server.js                        # Servidor Express
│   ├── package.json                     # Dependências Node
│   └── .env                             # Variáveis de ambiente
│
├── 📂 frontend/                         # Frontend React (New Farol)
│   ├── 📂 src/
│   │   ├── 📂 components/               # Componentes React
│   │   │   ├── 📂 Dashboard/           # Componentes do Dashboard
│   │   │   ├── 📂 Modal/                # Modais
│   │   │   ├── 📂 Farol/                # Componentes de Farol
│   │   │   └── ...
│   │   │
│   │   ├── 📂 pages/                    # Páginas
│   │   │   ├── ActiveProjects.tsx
│   │   │   ├── CompletedProjects.tsx
│   │   │   ├── FeatureDetails.tsx
│   │   │   ├── Login.tsx
│   │   │   └── ServiceUp.tsx
│   │   │
│   │   ├── 📂 hooks/                    # Custom Hooks
│   │   │   └── useServiceUpDateFilter.ts
│   │   │
│   │   ├── 📂 services/                 # Serviços de API
│   │   │   ├── api.ts                   # Cliente API principal
│   │   │   └── api_v2.ts                # Cliente API v2
│   │   │
│   │   ├── 📂 contexts/                 # Context API
│   │   │   ├── AuthContext.tsx
│   │   │   └── ...
│   │   │
│   │   ├── 📂 utils/                    # Utilitários
│   │   │   ├── statusNormalization.ts
│   │   │   ├── farol.ts
│   │   │   └── ...
│   │   │
│   │   ├── App.tsx                      # Componente principal
│   │   └── main.tsx                     # Entry point
│   │
│   ├── package.json                     # Dependências Node
│   ├── vite.config.ts                   # Configuração Vite
│   └── tailwind.config.js               # Configuração Tailwind
│
├── 📂 Painel Service UP/                # Sistema ServiceUp (Independente)
│   ├── 📂 backend/                      # Backend Node.js/Express (ServiceUp)
│   │   ├── 📂 routes/
│   │   │   └── chamados.js              # Rotas de chamados
│   │   ├── 📂 db/
│   │   │   └── connection.js            # Conexão MySQL
│   │   ├── server.js
│   │   └── package.json
│   │
│   └── 📂 frontend/                     # Frontend React (ServiceUp)
│       ├── 📂 src/
│       │   ├── 📂 components/
│       │   ├── 📂 contexts/
│       │   ├── 📂 hooks/
│       │   └── ...
│       ├── package.json
│       └── vite.config.js
│
├── start.bat                            # Script de inicialização (Windows)
├── .gitignore                           # Arquivos ignorados pelo Git
└── README.md                            # Este arquivo
```

---

<a id="api-endpoints"></a>
## 📚 API Endpoints {#api-endpoints}

### 🔐 Autenticação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/auth/login` | Inicia fluxo OAuth Microsoft |
| `GET` | `/api/auth/callback` | Callback OAuth |
| `GET` | `/api/auth/me?token=<token>` | Informações do usuário autenticado |

### 📊 Features

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/features` | Lista Features (com filtros opcionais) |
| `GET` | `/api/features/:id` | Detalhes de uma Feature |
| `GET` | `/api/features/:id/revisions` | Revisões e comentários |
| `GET` | `/api/features/:id/relations` | Relações da Feature |
| `GET` | `/api/features/:id/children` | Filhos (User Stories e Tasks) |
| `GET` | `/api/features/:id/attachments` | Anexos |
| `GET` | `/api/features/:id/links` | Links externos |
| `GET` | `/api/features/counts/wiql` | Contagens via WIQL |
| `GET` | `/api/features/open/wiql` | Features em aberto via WIQL |
| `GET` | `/api/features/closed/wiql` | Features encerradas via WIQL |
| `GET` | `/api/features/by-state/wiql` | Features agrupadas por estado |
| `GET` | `/api/features/by-farol/wiql` | Features agrupadas por Farol |
| `GET` | `/api/features/status/list` | Lista de status disponíveis |
| `GET` | `/api/features/pmo/list` | Lista de PMOs |
| `GET` | `/api/features/responsible/list` | Lista de responsáveis |

### 🏢 Clientes

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/clients/valid` | Clientes válidos (extraídos de Epics) |
| `GET` | `/api/v2/clients` | Clientes válidos (v2) |

### 📦 Work Items

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/work-items/bugs` | Lista de Bugs |
| `GET` | `/api/work-items/bugs/summary` | Resumo de Bugs |
| `GET` | `/api/work-items/tasks` | Lista de Tasks |
| `GET` | `/api/work-items/tasks/summary` | Resumo de Tasks |
| `GET` | `/api/work-items/user-stories` | Lista de User Stories |
| `GET` | `/api/work-items/by-type` | Work Items agrupados por tipo |
| `GET` | `/api/work-items/features/overdue` | Features atrasadas |
| `GET` | `/api/work-items/features/near-deadline` | Features próximas do prazo |
| `GET` | `/api/work-items/burndown` | Dados de burndown |

### 📤 Exportação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/export/features/export` | Exporta Features para Excel |

### 📈 Relatórios

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/reports/execute` | Executa relatório personalizado |

### 🔔 Webhooks

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/webhooks/azdo` | Recebe eventos do Azure DevOps (Service Hooks) |

### 🎯 Endpoint Consolidado (Recomendado)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/azdo/consolidated` | **Endpoint principal** que retorna todos os dados necessários para o Dashboard em uma única chamada |

**Exemplo de Resposta:**
```json
{
  "meta": {
    "org": "qualiit",
    "project": "Quali IT - Inovação e Tecnologia",
    "generated_at": "2025-12-17T10:00:00Z"
  },
  "totals": {
    "total_projects": 444,
    "open_projects": 303,
    "overdue_projects": 29,
    "near_deadline_projects": 4,
    "closed_projects": 141
  },
  "lists": {
    "total_projects": [...],
    "open_projects": [...],
    "overdue_projects": [...],
    "near_deadline_projects": [...],
    "closed_projects": [...]
  },
  "clients": {
    "summary": [...],
    "count": 15
  },
  "pmos": {
    "items": [...],
    "count": 14
  },
  "features_by_status": {...}
}
```

---

<a id="integracao-com-azure-devops"></a>
## 🔌 Integração com Azure DevOps {#integracao-com-azure-devops}

### WIQL (Work Item Query Language)

O sistema utiliza **WIQL** para consultar dados diretamente do Azure DevOps, garantindo precisão e consistência. WIQL é a linguagem de consulta nativa do Azure DevOps.

#### Padrão de Execução

Todos os endpoints seguem o padrão obrigatório de duas etapas:

1. **WIQL (Work Item Query Language)**: Executa query WIQL via POST para obter IDs dos Work Items
2. **Hidratação**: Busca detalhes completos usando GET workitems?ids=... com os campos necessários

Este padrão garante que os dados sejam sempre consistentes com o Azure DevOps e otimiza a performance através de processamento em paralelo quando possível.

#### Queries Principais

- **Features em aberto**: Features com estados não fechados (`State <> 'Closed'`)
- **Features atrasadas**: Features com Target Date vencido (`TargetDate < @Today`)
- **Features próximas do prazo**: Features com Target Date nos próximos 7 dias
- **Epics**: Para validação de clientes válidos

#### Validação de Clientes

O sistema valida Features contra Epics em aberto:
- Extrai clientes dos Epics via `AreaPath`
- Aceita Features com `AreaPath` válido (modo flexível)
- Filtra Features sem cliente associado

#### Exemplo de Query WIQL

```wiql
SELECT [System.Id], [System.Title], [System.State]
FROM WorkItems
WHERE [System.TeamProject] = @project
  AND [System.WorkItemType] = 'Feature'
  AND [System.State] <> 'Closed'
ORDER BY [Microsoft.VSTS.Scheduling.TargetDate]
```

### Personal Access Token (PAT)

#### Criar PAT no Azure DevOps

1. Acesse: **Azure DevOps** > **User settings** > **Personal access tokens**
2. Clique em **"New Token"**
3. Configure:
   - **Name**: `NewFarol Access`
   - **Organization**: `qualiit`
   - **Expiration**: Escolha um período
   - **Scopes**: 
     - ✅ **Code (Read & write)**
     - ✅ **Work Items (Read)**
4. Clique em **"Create"** e copie o token
5. Adicione no `.env`: `AZDO_PAT=seu-token-aqui`

⚠️ **Importante**: 
- O token só aparece uma vez - guarde-o com segurança
- Configure um lembrete para renovar antes de expirar
- Use tokens com escopo mínimo necessário

### Service Hooks (Webhooks)

O sistema suporta recebimento de eventos em tempo real do Azure DevOps.

#### Configuração no Azure DevOps

1. **Acessar Service Hooks**
   - Acesse o projeto no Azure DevOps
   - Vá em **Project Settings** (ícone de engrenagem)
   - No menu lateral, clique em **Service hooks**

2. **Criar Subscription**
   - Clique em **"Create subscription"**
   - Selecione **Web Hooks** como serviço
   - Configure o evento:
     - `Work item created`
     - `Work item updated`
     - `Work item deleted`
   - Configure a URL: `https://seu-backend-url/webhooks/azdo`
   - Clique em **"Finish"**

#### Autenticação (Opcional)

Para maior segurança, configure autenticação nos webhooks:
- Adicione um header `Authorization: Bearer seu-token-secreto` no Azure DevOps
- O endpoint `/webhooks/azdo` valida o token automaticamente

---

<a id="autenticacao"></a>
## 🔐 Autenticação {#autenticacao}

O sistema utiliza **OAuth 2.0** com Azure AD (Microsoft Entra ID) para autenticação segura.

### Fluxo de Autenticação

```
1. Usuário clica em "Entrar com Microsoft"
   ↓
2. Redirecionamento para Azure AD
   ↓
3. Usuário faz login na Microsoft
   ↓
4. Azure AD redireciona para /api/auth/callback
   ↓
5. Backend valida token e cria sessão
   ↓
6. Frontend recebe token JWT
   ↓
7. Token armazenado e usado em requisições
```

### Controle de Acesso

O sistema implementa controle de acesso baseado em domínio de e-mail:

- **E-mails Quali IT** (`@qualiit.com.br`): 
  - ✅ Acesso total (admin)
  - ✅ Visualiza todos os projetos
  - ✅ Acesso a todas as funcionalidades

- **E-mails de clientes**: 
  - ✅ Acesso restrito aos projetos da empresa
  - ✅ Filtro automático por cliente
  - ✅ Visualização limitada

### Segurança

- 🔒 **JWT Tokens**: Tokens assinados com algoritmo HS256
- ⏱️ **Expiração**: Tokens expiram em 30 minutos (configurável)
- 🔄 **Refresh**: Renovação automática de tokens
- 🛡️ **CORS**: Configuração de CORS para segurança
- 🔐 **HTTPS**: Recomendado para produção

---

<a id="sistema-unificado"></a>
## 🎯 Sistema Unificado {#sistema-unificado}

O projeto integra dois sistemas **totalmente independentes** que funcionam de forma isolada:

### New Farol

- **Backend**: Node.js/Express na porta 8000
- **Frontend**: React/TypeScript na porta 5173
- **Função**: Gestão de projetos Azure DevOps
- **Responsável**: Marcelo Macedo
- **Pasta**: `backend/` e `frontend/`

### Painel Service UP

- **Backend**: Node.js/Express na porta 3000
- **Frontend**: React/JSX na porta 5174
- **Função**: Gestão de chamados
- **Responsável**: Davi Silva
- **Pasta**: `Painel Service UP/backend/` e `Painel Service UP/frontend/`

---

## 🔒 Independência Total dos Sistemas

### ⚠️ IMPORTANTE: Separação Completa

**Os dois sistemas são COMPLETAMENTE INDEPENDENTES e ISOLADOS entre si.**

### 📁 Estrutura de Pastas e Isolamento

```
NewFarol/
├── backend/                    ← NEW FAROL BACKEND
│   ├── routes/                 ← Rotas do New Farol
│   ├── utils/                  ← Utilitários do New Farol
│   └── server.js               ← Servidor do New Farol (porta 8000)
│
├── frontend/                   ← NEW FAROL FRONTEND
│   ├── src/
│   │   ├── components/         ← Componentes do New Farol
│   │   ├── pages/              ← Páginas do New Farol
│   │   └── services/           ← APIs do New Farol
│   └── vite.config.ts          ← Config do New Farol (porta 5173)
│
└── Painel Service UP/           ← PAINEL SERVICE UP (TOTALMENTE SEPARADO)
    ├── backend/                ← BACKEND DO SERVICEUP (INDEPENDENTE)
    │   ├── routes/             ← Rotas do ServiceUp
    │   └── server.js           ← Servidor do ServiceUp (porta 3000)
    │
    └── frontend/               ← FRONTEND DO SERVICEUP (INDEPENDENTE)
        ├── src/
        │   ├── components/     ← Componentes do ServiceUp
        │   └── services/       ← APIs do ServiceUp
        └── vite.config.js      ← Config do ServiceUp (porta 5174)
```

### 🎯 Regras de Isolamento

#### ✅ Alterações no New Farol

**O que você altera:**
- Arquivos em `backend/` (rotas, utilitários, server.js)
- Arquivos em `frontend/` (componentes, páginas, serviços)

**O que é afetado:**
- ✅ **Apenas** a página New Farol e suas subpáginas
- ✅ Dashboard do New Farol
- ✅ Lista de Features
- ✅ Detalhes de Features
- ✅ Relatórios do New Farol
- ✅ Todas as funcionalidades do New Farol

**O que NÃO é afetado:**
- ❌ **Painel Service UP** (permanece inalterado)
- ❌ Backend do ServiceUp (porta 3000)
- ❌ Frontend do ServiceUp (porta 5174)
- ❌ Qualquer arquivo dentro de `Painel Service UP/`

#### ✅ Alterações no Painel Service UP

**O que você altera:**
- Arquivos em `Painel Service UP/backend/` (rotas, conexões DB, server.js)
- Arquivos em `Painel Service UP/frontend/` (componentes, páginas, serviços)

**O que é afetado:**
- ✅ **Apenas** a página Painel Service UP
- ✅ Dashboard de chamados
- ✅ Relatórios de SLA
- ✅ Análises de satisfação
- ✅ Todas as funcionalidades do ServiceUp

**O que NÃO é afetado:**
- ❌ **New Farol** (permanece inalterado)
- ❌ Backend do New Farol (porta 8000)
- ❌ Frontend do New Farol (porta 5173)
- ❌ Qualquer arquivo fora de `Painel Service UP/`

### 🔗 Integração Visual (Apenas Exibição)

A única conexão entre os sistemas é **visual**, através de um `<iframe>`:

```typescript
// frontend/src/pages/ServiceUp.tsx (New Farol)
<iframe 
  src="http://localhost:5174"  // Frontend ServiceUp standalone
  style={{ width: '100%', height: '100vh' }}
/>
```

**Características da integração:**
- ✅ **Apenas visual**: O iframe apenas exibe o ServiceUp dentro do New Farol
- ✅ **Sem dependências**: Nenhum código é compartilhado
- ✅ **Sem comunicação**: Não há troca de dados entre os sistemas
- ✅ **Isolamento total**: Cada sistema roda em seu próprio servidor
- ✅ **Pode funcionar separadamente**: Cada sistema pode rodar sozinho

### 🚀 Execução Independente

#### New Farol pode rodar sozinho:

```bash
# Terminal 1 - Backend New Farol
cd backend
npm run dev  # Porta 8000

# Terminal 2 - Frontend New Farol
cd frontend
npm run dev  # Porta 5173
```

**Resultado**: New Farol funciona completamente, exceto a página `/serviceup` que não carregará.

#### Painel Service UP pode rodar sozinho:

```bash
# Terminal 1 - Backend ServiceUp
cd "Painel Service UP/backend"
npm run dev  # Porta 3000

# Terminal 2 - Frontend ServiceUp
cd "Painel Service UP/frontend"
npm run dev  # Porta 5174
```

**Resultado**: ServiceUp funciona completamente de forma standalone.

### 📝 Resumo da Independência

| Aspecto | New Farol | Painel Service UP |
|---------|-----------|-------------------|
| **Backend** | `backend/` (porta 8000) | `Painel Service UP/backend/` (porta 3000) |
| **Frontend** | `frontend/` (porta 5173) | `Painel Service UP/frontend/` (porta 5174) |
| **Banco de Dados** | Azure DevOps (via API) | MySQL (próprio) |
| **Dependências** | `backend/package.json` | `Painel Service UP/backend/package.json` |
| **Alterações** | Só afeta New Farol | Só afeta ServiceUp |
| **Desenvolvedor** | Marcelo Macedo | Davi Silva |
| **Linguagem Backend** | Node.js/Express | Node.js/Express |
| **Linguagem Frontend** | TypeScript/React | JavaScript/React |

### ✅ Garantias de Isolamento

1. **Pastas Separadas**: Cada sistema tem suas próprias pastas
2. **Portas Diferentes**: Cada sistema roda em portas diferentes
3. **Dependências Separadas**: Cada sistema tem seu próprio `package.json`
4. **Sem Imports Compartilhados**: Nenhum código é importado entre sistemas
5. **Backends Independentes**: Cada backend é um servidor Express separado
6. **Frontends Independentes**: Cada frontend é uma aplicação Vite separada
7. **Integração Apenas Visual**: A única conexão é via iframe HTML

### 🎯 Exemplo Prático

**Cenário 1: Alterar uma rota no New Farol**

```javascript
// backend/routes/features.js (New Farol)
router.get('/', async (req, res) => {
  // Sua alteração aqui
});
```

**Impacto:**
- ✅ Afeta apenas endpoints do New Farol
- ✅ Afeta apenas o frontend do New Farol
- ❌ **NÃO afeta** o ServiceUp de forma alguma

**Cenário 2: Alterar uma rota no ServiceUp**

```javascript
// Painel Service UP/backend/routes/chamados.js (ServiceUp)
router.get('/atendidos', async (req, res) => {
  // Sua alteração aqui
});
```

**Impacto:**
- ✅ Afeta apenas endpoints do ServiceUp
- ✅ Afeta apenas o frontend do ServiceUp
- ❌ **NÃO afeta** o New Farol de forma alguma

### 🔒 Conclusão

**Cada desenvolvedor pode trabalhar em seu sistema sem interferir no outro:**

- 👨‍💻 **Marcelo Macedo** trabalha em `backend/` e `frontend/` (New Farol)
- 👨‍💻 **Davi Silva** trabalha em `Painel Service UP/backend/` e `Painel Service UP/frontend/` (ServiceUp)
- ✅ **Zero conflitos**: Alterações em um sistema não afetam o outro
- ✅ **Deploy independente**: Cada sistema pode ser deployado separadamente
- ✅ **Manutenção isolada**: Problemas em um sistema não afetam o outro

---

<a id="git-submodules"></a>
## 🔗 Git Submodules {#git-submodules}

### Visão Geral

O **Painel Service UP** está vinculado ao repositório **New Farol** como um **Git Submodule**, permitindo que os dois repositórios sejam mantidos separadamente enquanto o Service UP é referenciado dentro do New Farol.

### 📚 Repositórios Vinculados

- **New Farol**: `https://dev.azure.com/qualiit/ALM/_git/Qualiit.Portal.New.Farol`
- **Painel Service UP**: `https://dev.azure.com/qualiit/ALM/_git/Qualiit.Portal.Clientes.v2` (submodule)

### ✅ Como Funciona

1. **Repositórios Separados**: Cada sistema mantém seu próprio histórico Git
2. **Referência Específica**: O submodule referencia um commit específico do Service UP
3. **Atualização Manual**: Você controla quando atualizar o Service UP dentro do New Farol
4. **Independência Total**: Alterações no repositório Service UP não afetam automaticamente o New Farol

### 🚀 Clonando o Repositório pela Primeira Vez

Ao clonar o repositório New Farol, você precisa inicializar os submodules:

```bash
# Clonar com submodules recursivamente (RECOMENDADO)
git clone --recurse-submodules https://dev.azure.com/qualiit/ALM/_git/Qualiit.Portal.New.Farol

# OU se já clonou sem submodules
git clone https://dev.azure.com/qualiit/ALM/_git/Qualiit.Portal.New.Farol
cd Qualiit.Portal.New.Farol
git submodule init
git submodule update
```

### 🔄 Atualização automática do Painel Service UP

A pasta **Painel Service UP** é sincronizada com o repositório do Davi Silva (`Qualiit.Portal.Clientes.v2`) **automaticamente**, sem precisar rodar scripts locais:

- **Workflow** `.github/workflows/update-serviceup.yml`: roda **todo dia** (agendado) e pode ser disparado **manualmente** (Actions → "Atualizar Painel Service UP" → Run workflow).
- Após o workflow rodar, as alterações são commitadas e enviadas ao repositório; um `git pull` traz a pasta atualizada.

**Secrets (repositório privado):** configurar no GitHub/Azure o secret **SERVICEUP_SYNC_TOKEN** ou **AZURE_DEVOPS_PAT** (PAT com permissão de leitura no repo `Qualiit.Portal.Clientes.v2` e de escrita no repo New Farol, para o push).

**Arquivos .bat:** os arquivos `*.bat` (ex.: `update-serviceup.bat`, `start.bat`) **não são versionados** (estão no `.gitignore`). Podem ser usados apenas localmente; a sincronização em produção é feita pelo workflow.

### 📝 Fluxo de Trabalho

#### Para Davi Silva (Painel Service UP)
1. Trabalha normalmente no repositório `Qualiit.Portal.Clientes.v2`
2. Faz commits e push normalmente
3. **Não precisa** fazer nada no repositório New Farol — o workflow atualiza a pasta automaticamente

#### Para quem mantém o New Farol
1. Basta dar **pull** no repositório; a pasta `Painel Service UP` já vem atualizada pelo workflow (ou disparar o workflow manualmente nas Actions)
2. Não é necessário rodar nenhum `.bat` para sincronizar

### ⚠️ Comandos Úteis

```bash
# Ver o status dos submodules
git submodule status

# Atualizar todos os submodules
git submodule update --remote

# Ver o commit atual do submodule
cd "Painel Service UP"
git log -1
```

### 🔧 Configuração Inicial (Primeira Vez)

Se você clonou este repositório e a pasta `Painel Service UP/` está vazia ou não funciona, siga estes passos:

#### 1. Remover a pasta atual (se necessário)

```bash
# Se a pasta já existe e não é um submodule, remova-a para adicionar corretamente
git rm -r --cached "Painel Service UP"
rm -rf "Painel Service UP"  # Linux/macOS
# ou rmdir /s /q "Painel Service UP"  # Windows
```

#### 2. Adicionar como Submodule

```bash
# Adicionar o repositório Service UP como submodule
git submodule add https://dev.azure.com/qualiit/ALM/_git/Qualiit.Portal.Clientes.v2 "Painel Service UP"
```

#### 3. Inicializar e Atualizar

```bash
# Inicializar e atualizar os submodules
git submodule update --init --recursive
```

#### 4. Commitar

```bash
git add .gitmodules "Painel Service UP"
git commit -m "Add Painel Service UP as submodule"
git push origin main
```

### ⚠️ Troubleshooting

**Submodule aparece como "modified" mesmo sem alterações:**
```bash
cd "Painel Service UP"
git status
# Se não houver alterações, volte e faça:
cd ..
git submodule update
```

**Submodule vazio após clonar:**
```bash
git submodule init
git submodule update
```

**Não consigo fazer push do submodule:**
```bash
# O submodule é um repositório separado
# Faça push no repositório Service UP primeiro
cd "Painel Service UP"
git push origin main
# Depois atualize a referência no New Farol
cd ..
git add "Painel Service UP"
git commit -m "Update submodule"
git push origin main
```

### ✅ Vantagens

- ✅ **Repositórios separados** - Cada desenvolvedor trabalha no seu próprio repositório
- ✅ **Histórico preservado** - Histórico completo de cada projeto mantido separadamente
- ✅ **Versionamento claro** - Cada versão do New Farol referencia uma versão específica do Service UP
- ✅ **Rollback fácil** - Pode voltar para versões anteriores do Service UP se necessário
- ✅ **Sem duplicação** - Não duplica arquivos, apenas referencia o repositório

---

<a id="desenvolvimento"></a>
## 🛠️ Desenvolvimento {#desenvolvimento}

<details>
<summary><strong>🟢 Desenvolvimento Backend</strong></summary>

#### Executar em Modo Desenvolvimento

```bash
cd backend
npm run dev
```

O servidor será reiniciado automaticamente quando arquivos forem modificados (usando `--watch`).

#### Estrutura de Rotas

As rotas estão organizadas em módulos separados:

- `routes/auth.js` - Autenticação
- `routes/features.js` - Features
- `routes/workItems.js` - Work Items
- `routes/azdo.js` - Endpoint consolidado
- `routes/projects.js` - Projetos
- `routes/reports.js` - Relatórios
- `routes/export.js` - Exportação
- `routes/webhooks.js` - Webhooks
- `routes/clients.js` - Clientes
- `routes/featuresAnalytics.js` - Analytics
- `routes/featuresV2.js` - API v2

#### Utilitários

- `utils/wiql.js` - Queries WIQL
- `utils/wiqlClient.js` - Cliente WIQL
- `utils/normalization.js` - Normalização de dados
- `utils/ttlCache.js` - Cache TTL
- `utils/azureDevOpsClientExtended.js` - Cliente Azure DevOps
- `utils/auth.js` - Utilitários de autenticação

</details>

<details>
<summary><strong>⚛️ Desenvolvimento Frontend</strong></summary>

#### Executar em Modo Desenvolvimento

```bash
cd frontend
npm run dev
```

#### Linting

```bash
npm run lint
```

#### Build de Produção

```bash
npm run build
```

Os arquivos serão gerados em `frontend/dist/`.

#### Preview de Produção

```bash
npm run preview
```

#### Limpar Cache

```bash
# Remover cache do Vite
rm -rf node_modules/.vite
rm -rf dist

# Limpar node_modules (se necessário)
rm -rf node_modules
npm install
```

</details>

---

<a id="solucao-de-problemas"></a>
## 🐛 Solução de Problemas {#solucao-de-problemas}

<details>
<summary><strong>🔧 Backend não está disponível</strong></summary>

#### Problema: Servidor não inicia

**Solução:**
1. Verifique se o servidor está rodando:
   ```bash
   cd backend
   npm run dev
   ```

2. Verifique se a porta 8000 está livre:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Linux/Mac
   lsof -i :8000
   ```

3. Verifique se todas as dependências estão instaladas:
   ```bash
   cd backend
   npm install
   ```

4. Verifique os logs do servidor para identificar erros específicos

#### Problema: Erro de importação

**Solução:**
- Certifique-se de que todas as dependências estão instaladas
- Execute: `npm install`
- Verifique se está usando Node.js 18+

</details>

<details>
<summary><strong>🌐 Frontend não conecta ao backend</strong></summary>

#### Problema: Erro de CORS

**Solução:**
1. Verifique se o backend está rodando na porta 8000
2. Verifique o `CORS_ORIGINS` no `.env` do backend (ou configuração no `server.js`)
3. Reinicie o servidor backend

#### Problema: Erro 404 nas requisições

**Solução:**
1. Verifique o proxy no `vite.config.ts`
2. Verifique se o backend está rodando
3. Limpe o cache do navegador (Ctrl+Shift+R)

</details>

<details>
<summary><strong>📊 Dados incorretos no Dashboard</strong></summary>

#### Problema: Números divergentes

**Solução:**
1. Verifique o PAT do Azure DevOps - deve ter permissões de leitura
2. Verifique os logs do backend para identificar problemas
3. Limpe o cache do frontend (React Query)

#### Problema: PMOs ou Clientes não aparecem

**Solução:**
1. Verifique se os dados estão sendo extraídos corretamente do Azure DevOps
2. Verifique os logs do backend
3. Verifique se o PAT tem permissões corretas

</details>

<details>
<summary><strong>🔐 Erro de autenticação OAuth</strong></summary>

#### Problema: "redirect_uri_mismatch"

**Solução:**
1. Verifique as variáveis de ambiente do Azure AD
2. Confirme o Redirect URI no Azure Portal:
   - Backend: `http://localhost:8000/api/auth/callback`
   - Frontend: `http://localhost:5173/auth/success`
3. Certifique-se de que os URIs estão configurados corretamente no Azure AD

#### Problema: "invalid_client"

**Solução:**
1. Verifique se o Client Secret está correto no `.env`
2. Verifique se o Client Secret não expirou
3. Crie um novo Client Secret se necessário

</details>

<details>
<summary><strong>🚀 Script start.bat não funciona</strong></summary>

#### Problema: Janela fecha imediatamente

**Solução:**
1. Verifique se Node.js está instalado:
   ```bash
   node --version
   ```

2. Execute o script manualmente e verifique os erros:
   ```bash
   start.bat
   ```

3. Verifique se todas as pastas existem:
   - `backend/`
   - `frontend/`
   - `Painel Service UP/backend/`
   - `Painel Service UP/frontend/`

</details>

<details>
<summary><strong>🧹 Limpar Cache</strong></summary>

#### Backend (Cache em Memória)

O cache do backend está em **memória**, então ao reiniciar o servidor, o cache é limpo automaticamente.

#### Frontend (React Query Cache)

**Opção 1: Hard Refresh**
- **Chrome/Edge**: `Ctrl + Shift + R` ou `Ctrl + F5`
- **Firefox**: `Ctrl + Shift + R` ou `Ctrl + F5`
- **Safari**: `Cmd + Shift + R`

**Opção 2: Via Console do Navegador**
```javascript
// Limpar cache do React Query
localStorage.clear();
sessionStorage.clear();
location.reload();
```

</details>

---

<a id="deploy"></a>
## 🚀 Deploy {#deploy}

**Troca de produção (Portal Clientes → New Farol):** para substituir a aplicação antiga pela New Farol no **mesmo link de produção** e desativar a antiga, use o guia **[DEPLOY.md](DEPLOY.md)** (passos para inativar o Portal Clientes e subir a New Farol com Docker no mesmo host/URL).

<details>
<summary><strong>🐳 Deploy com Docker (recomendado para produção)</strong></summary>

Na raiz do repositório:

```bash
# Configurar backend/.env (copiar de backend/.env.example e preencher FRONTEND_URL, AZURE_AD_*, etc.)
cp backend/.env.example backend/.env

# Build e subir frontend (porta 80) + backend
docker compose up -d --build
```

O frontend (nginx) expõe a porta 80; `/api` e `/webhooks` são repassados para o backend. Detalhes e passos para troca de produção: [DEPLOY.md](DEPLOY.md).

</details>

<details>
<summary><strong>🔧 Deploy do Backend</strong></summary>

#### 1. Preparar Ambiente

```bash
# Instalar dependências
cd backend
npm install --production
```

#### 2. Configurar Variáveis de Ambiente

Copie `.env.example` para `.env` e configure todas as variáveis necessárias.

#### 3. Iniciar Servidor

**Desenvolvimento:**
```bash
npm run dev
```

**Produção:**
```bash
npm start
```

**Produção com PM2 (Recomendado):**
```bash
npm install -g pm2
pm2 start server.js --name newfarol-backend
pm2 save
pm2 startup
```

#### 4. Configurar Nginx (Opcional)

```nginx
server {
    listen 80;
    server_name api.newfarol.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

</details>

<details>
<summary><strong>🎨 Deploy do Frontend</strong></summary>

#### 1. Build de Produção

```bash
cd frontend
npm run build
```

Os arquivos serão gerados em `frontend/dist/`.

#### 2. Servir Arquivos

**Opção 1: Nginx**
```nginx
server {
    listen 80;
    server_name newfarol.com;
    root /path/to/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Opção 2: Apache**
```apache
<VirtualHost *:80>
    ServerName newfarol.com
    DocumentRoot /path/to/frontend/dist

    <Directory /path/to/frontend/dist>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
```

**Opção 3: Servidor Estático (Node.js)**
```bash
npm install -g serve
serve -s dist -l 3000
```

</details>

<details>
<summary><strong>📦 Azure Repos</strong></summary>

- **Repositório atual (New Farol):** https://dev.azure.com/qualiit/ALM/_git/Qualiit.Portal.New.Farol  
- **Projeto anterior (Portal Clientes):** https://dev.azure.com/qualiit/ALM/_git/Qualiit.Portal.Clientes — não é alterado; apenas a aplicação em produção é desativada no servidor quando a New Farol assume o mesmo link (ver [DEPLOY.md](DEPLOY.md)).

Para fazer push de alterações:

```bash
git add .
git commit -m "Descrição das alterações"
git push origin main
```

</details>

---

<a id="documentacao"></a>
## 📖 Documentação {#documentacao}

### Documentação da API

A documentação da API está disponível através dos endpoints:

- **Health Check**: http://localhost:8000/health
- **API Info**: http://localhost:8000/api

### Documentação do Código

- **Backend**: Documentação inline em JavaScript (comentários JSDoc)
- **Frontend**: Documentação inline em TypeScript (JSDoc)
- **README**: Este arquivo

### Recursos Adicionais

- [Express Documentation](https://expressjs.com/)
- [React Documentation](https://react.dev/)
- [Azure DevOps REST API](https://learn.microsoft.com/en-us/rest/api/azure/devops/)
- [WIQL Syntax](https://learn.microsoft.com/en-us/azure/devops/boards/queries/wiql-syntax)

---

<a id="contribuindo"></a>
## 🤝 Contribuindo {#contribuindo}

Contribuições são bem-vindas! Siga estes passos:

### 1. Fork o Projeto

```bash
git clone https://dev.azure.com/qualiit/ALM/_git/Qualiit.Portal.Clients.v3
cd NewFarol
```

### 2. Crie uma Branch

```bash
git checkout -b feature/nova-feature
```

### 3. Faça suas Alterações

- Siga os padrões de código estabelecidos
- Adicione testes para novas funcionalidades
- Atualize a documentação se necessário

### 4. Commit suas Mudanças

```bash
git add .
git commit -m "feat: Adiciona nova feature"
```

**Convenção de Commits:**
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `style:` Formatação
- `refactor:` Refatoração
- `test:` Testes
- `chore:` Manutenção

### 5. Push para a Branch

```bash
git push origin feature/nova-feature
```

### 6. Abra um Pull Request

Crie um Pull Request no Azure DevOps descrevendo suas alterações.

---

<a id="licenca"></a>
## 📄 Licença {#licenca}

Este projeto é **proprietário** da **Quali IT - Inovação e Tecnologia**.

Todos os direitos reservados. Este software não pode ser copiado, modificado, distribuído ou usado sem autorização expressa.

---

## 👥 Equipe

**Desenvolvido por**: Quali IT - Inovação e Tecnologia

### Responsabilidades por Sistema

**New Farol** - Marcelo Macedo
- ✅ Responsável por `backend/` e `frontend/`
- ✅ Todas as alterações no New Farol
- ✅ Manutenção e desenvolvimento do sistema de gestão Azure DevOps

**Painel Service UP** - Davi Silva
- ✅ Responsável por `Painel Service UP/backend/` e `Painel Service UP/frontend/`
- ✅ Todas as alterações no ServiceUp
- ✅ Manutenção e desenvolvimento do sistema de gestão de chamados

### ⚠️ Importante

**Cada desenvolvedor mantém seu próprio sistema de forma independente. Alterações em um sistema não afetam o outro.**

**Contato**: Entre em contato com a equipe de desenvolvimento para suporte.

---

<a id="historico-de-versoes"></a>
## 📋 Histórico de versões

A numeração **2.x** refere-se ao **New Farol** (este repositório). O projeto anterior é o **Portal Clientes** ([Qualiit.Portal.Clientes](https://dev.azure.com/qualiit/ALM/_git/Qualiit.Portal.Clientes)), que foi evoluído para esta plataforma a partir da versão 2.0.0.

| Versão | Data | Alterações |
|--------|------|------------|
| 2.3.0 | 09-10/02/2026 | Redirect de login por origem (return_origin). OAuth2 completo com Microsoft Entra ID (troca código por token, id_token, JWT). is_admin por domínio (@qualiit.com.br). Acesso B2B: convidados no tenant Quali IT, atribuição só ao app Farol, doc. one-time passcode. Correções: navbar duplicada no Painel Service Up (oculta em iframe), logo Quali IT (public/logo-qualiit.svg). Doc: permissões Entra ID, app Web (não cliente público), tokens implícitos, passo a passo B2B. Histórico de versões em tabela. |
| 2.2.0 | 12/01/2026 | Sincronização Painel Service UP com repositório (Davi Silva). Atualização de scripts e configuração de portas. Update submodule Painel Service UP. |
| 2.1.0 | 11/01/2026 | Consolidação de documentação em README.md. Remoção de arquivos .md desnecessários. READMEOLD no .gitignore. |
| 2.0.0 | 08/01/2026 | Início do New Farol. Migração completa do backend Python para Node.js. ServiceUp via iframe (independência total). Arquivos .env.example para ambos os backends. README e ENV_SETUP. Correções de imports, proxy Vite, baseURL da API, connection.js. Garantia de independência New Farol / Painel Service UP. Estrutura frontend ServiceUp independente. |
| Portal Clientes (anterior) | — | Portal legado; evoluído para New Farol 2.0.0. Repositório: [Qualiit.Portal.Clientes](https://dev.azure.com/qualiit/ALM/_git/Qualiit.Portal.Clientes). |

---

## 📞 Suporte

Para suporte, dúvidas ou problemas:

1. Verifique a seção [Solução de Problemas](#-solução-de-problemas)
2. Consulte a [Documentação](#-documentação)
3. Entre em contato com a equipe de desenvolvimento

---

<div align="center">

**Última atualização**: 09/02/2026  
**Versão**: 2.3.0
**Backend**: Node.js/Express  
**Frontend**: React/TypeScript  
**Desenvolvido por**: Marcelo Macedo  
**E-mail**: [marcelo.macedo@qualiit.com.br](mailto:marcelo.macedo@qualiit.com.br)

---

⭐ **Se este projeto foi útil, considere dar uma estrela!** ⭐

</div>
