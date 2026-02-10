# Cursor.ai Configuration Files

Arquivos de configuração otimizados para desenvolvimento com Python, JavaScript/TypeScript, React, Node.js, Power BI, SQL, PostgreSQL, Progress/OpenEdge e DevOps.

## Estrutura

```
.cursorrules/
├── 00-foundation.mdc          # ✅ Regras globais (sempre ativo)
├── 01-architecture.mdc         # ✅ Arquitetura (sempre ativo)
├── 10-python.mdc              # Python 3.10+, tipagem, async, testes
├── 11-data-engineering.mdc    # SQL, PostgreSQL, ETL, performance
├── 12-progress-openedge.mdc   # Progress/OpenEdge, extração, mapeamento
├── 20-frontend.mdc            # JS/TS, React, Node.js, padrões frontend
├── 30-powerbi.mdc             # Power BI, DAX, powerbi-modeling-mcp
├── 40-devops.mdc              # Pipelines CI/CD, YAML, segurança
├── 50-git-autopush.mdc        # ✅ Commit e push automáticos (origin + azure)
└── 99-workflows.mdc           # Commit, deploy, hotfix, code review
```

## Arquivos por Categoria

### 🎯 Sempre Ativos (`alwaysApply: true`)

Carregados automaticamente em toda interação:

- **00-foundation.mdc**: Postura, comunicação técnica, princípios de código, segurança
- **01-architecture.mdc**: Separação de camadas, DDD tático, anti-patterns, ADRs
- **50-git-autopush.mdc**: Após qualquer alteração, commit + push para **origin** (GitHub) e **azure** (Azure Repos)

### 🐍 Python

- **10-python.mdc**: Type hints, pydantic, dataclasses, async/await, logging, testes (pytest), ferramentas (ruff, mypy)

### 📊 Data Engineering

- **11-data-engineering.mdc**: 
  - SQL: CTEs, joins, segurança (parametrização)
  - PostgreSQL: modelagem, tipos, índices, migrações
  - ETL: chunks, idempotência, validação, métricas
  
- **12-progress-openedge.mdc**: Mapeamento de tipos, extração (ODBC/dump), encoding, estratégias de upsert

### 🌐 Frontend & Backend

- **20-frontend.mdc**:
  - TypeScript: tipos explícitos, imutabilidade, tratamento de erros
  - React: hooks customizados, performance (memoização consciente), acessibilidade
  - Node.js: estrutura em camadas, validação (zod), observabilidade

### 📈 Business Intelligence

- **30-powerbi.mdc**: 
  - Modelagem star schema
  - DAX: VAR, SWITCH vs IF, time intelligence
  - powerbi-modeling-mcp: workflow, validação, comunicação

### 🚀 DevOps

- **40-devops.mdc**: 
  - Pipelines: idempotência, fail fast, separação de etapas
  - YAML: templates, variáveis, secrets
  - CI/CD: cache, paralelismo, segurança

### 📝 Workflows

- **99-workflows.mdc** (⚠️ invocação explícita):
  - Git: Conventional Commits, estratégia de branches
  - Deploy: checklist pré/pós-deploy, rollback
  - Hotfix: procedimento de emergência
  - Manutenção: dependências, auditoria

---

## Como Usar

### Instalação

1. **Copiar arquivos** para o diretório de configuração do Cursor.ai:
   ```bash
   cp *.mdc ~/.cursor/rules/
   ```

2. **Verificar** que Cursor.ai reconhece os arquivos:
   - Abrir Cursor.ai
   - Settings → Rules → Verificar lista de arquivos

### Comportamento

#### Automático
Cursor.ai carrega automaticamente:
- `00-foundation.mdc` e `01-architecture.mdc` sempre
- Arquivos específicos de tecnologia quando detecta o contexto:
  - `.py` → `10-python.mdc`
  - `.sql`, menção de "ETL" → `11-data-engineering.mdc`
  - `.ts`, `.tsx`, `.jsx` → `20-frontend.mdc`
  - Menção de "Power BI", "DAX" → `30-powerbi.mdc`
  - `.yml`, `.yaml` → `40-devops.mdc`

#### Manual
Para workflows específicos, mencionar explicitamente:
- "Siga o workflow de commit do arquivo 99-workflows"
- "Aplique o checklist de deploy"

---

## Exemplos de Uso

### Python
```
User: "Criar função para validar email"
Cursor: [carrega 00-foundation + 01-architecture + 10-python]
```

Resultado esperado:
```python
from pydantic import BaseModel, EmailStr, Field

class UserInput(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    
def validate_user_email(email: str) -> bool:
    """Validate email format using pydantic.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ValidationError: If email format is invalid
    """
    try:
        UserInput(email=email)
        return True
    except ValidationError:
        return False
```

### SQL
```
User: "Query para listar usuários ativos com total de pedidos"
Cursor: [carrega 00-foundation + 01-architecture + 11-data-engineering]
```

Resultado esperado:
```sql
WITH active_users AS (
    SELECT user_id, email
    FROM users
    WHERE last_login >= CURRENT_DATE - INTERVAL '30 days'
        AND status = 'active'
),
user_order_counts AS (
    SELECT 
        user_id,
        COUNT(DISTINCT order_id) as total_orders
    FROM orders
    WHERE status = 'completed'
    GROUP BY user_id
)
SELECT 
    au.email,
    COALESCE(uoc.total_orders, 0) as orders
FROM active_users au
LEFT JOIN user_order_counts uoc ON au.user_id = uoc.user_id
ORDER BY orders DESC;
```

### React
```
User: "Componente de lista de usuários com loading state"
Cursor: [carrega 00-foundation + 01-architecture + 20-frontend]
```

Resultado esperado:
```typescript
interface User {
  id: string;
  name: string;
  email: string;
}

function useFetchUsers(): {
  users: User[];
  loading: boolean;
  error: Error | null;
} {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    fetch('/api/users')
      .then(res => res.json())
      .then(setUsers)
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);

  return { users, loading, error };
}

export function UserList() {
  const { users, loading, error } = useFetchUsers();

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>
          {user.name} ({user.email})
        </li>
      ))}
    </ul>
  );
}
```

---

## Customização

### Adicionar Nova Tecnologia

1. **Escolher número** adequado:
   - 10-19: Linguagens backend
   - 20-29: Frontend/fullstack
   - 30-39: Ferramentas específicas (BI, etc.)
   - 40-49: DevOps/infraestrutura

2. **Criar arquivo** seguindo template:
   ```markdown
   ---
   description: "Breve descrição da tecnologia"
   alwaysApply: false
   ---
   
   # Nome da Tecnologia
   
   ## Seção 1
   
   ### Subseção com Exemplos
   
   ```language
   // ✅ Bom
   code_example();
   
   // ❌ Evitar
   bad_code_example();
   ```
   ```

3. **Testar** com projeto real

### Modificar Arquivo Existente

1. **Manter estrutura** de seções
2. **Adicionar exemplos** práticos (✅/❌)
3. **Evitar duplicação** com outros arquivos
4. **Testar** que Cursor.ai aplica corretamente

---

## Troubleshooting

### Cursor.ai não está seguindo as regras

1. **Verificar** que arquivo tem `alwaysApply: true` (se deve ser sempre ativo)
2. **Mencionar explicitamente**: "Use as convenções do arquivo 10-python.mdc"
3. **Verificar conflitos** entre arquivos (dois arquivos com instruções opostas)

### Respostas muito longas/verbosas

- Revisar `00-foundation.mdc` → seção "Postura e Comunicação"
- Garantir: "tom direto e técnico", "evitar explicações básicas"

### Código não está production-grade

- Verificar que `00-foundation.mdc` está ativo
- Princípio: "Código deve ser production-grade: legível, testável, com tratamento de erro"

---

## Contribuindo

### Reportar Problema

1. Identificar qual arquivo contém a instrução problemática
2. Descrever comportamento esperado vs. observado
3. Incluir exemplo de prompt e resposta do Cursor.ai

### Sugerir Melhoria

1. Identificar arquivo a ser melhorado
2. Propor mudança específica (adicionar seção, modificar exemplo)
3. Justificar benefício (clareza, correção, performance)

---

## Changelog

### v2.0.0 (2025-02-09)
- ♻️ Reestruturação completa: 16 → 8 arquivos
- ✨ Consolidações: SQL+PostgreSQL+ETL, JS/TS+React+Node, Pipelines+YAML
- 🔥 Removidos: `repo-conventions` (redundante), `commit-and-push` automático (perigoso)
- ✏️ Expandidos: Python, Power BI, Progress/OpenEdge com exemplos práticos
- 📝 Novo: `99-workflows.mdc` para procedimentos manuais
- 🎯 Filosofia: Prescritivo com exemplos (✅/❌) ao invés de apenas descritivo

### v1.0.0 (Anterior)
- 📦 16 arquivos separados
- ⚠️ Duplicação de conteúdo entre arquivos
- 📄 Instruções descritivas sem exemplos

---

## Licença

Estes arquivos de configuração são de uso pessoal/interno. Sinta-se livre para adaptar ao seu contexto.

---

## Suporte

Para dúvidas ou problemas:
1. Revisar este README
2. Consultar `ANALYSIS.md` para detalhes técnicos da reestruturação
3. Verificar exemplos de uso acima
