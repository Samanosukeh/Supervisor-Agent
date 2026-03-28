<div align="center">

# 🎯 Supervisor Agent

### Multi-Agent Orchestration with LangGraph

<br>

```
                         ┌─────────────┐
                         │   Usuário   │
                         └──────┬──────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │     🧠 SUPERVISOR     │
                    │    ┌───────────────┐  │
                    │    │ Mistral Large │  │
                    │    │  "Quem faz?"  │  │
                    │    └───────────────┘  │
                    └──┬────────┬────────┬──┘
                       │        │        │
              ┌────────┘        │        └────────┐
              ▼                 ▼                  ▼
     ┌────────────────┐ ┌──────────────┐ ┌────────────────┐
     │  🔍 Pesquisador│ │ 🧮 Matemático│ │  ✍️  Escritor   │
     │  web_search    │ │ calculator   │ │  generate      │
     │  fetch_url     │ │ plot_chart   │ │  summarize     │
     │ Mistral Small  │ │ Mistral Small│ │ Mistral Small  │
     └────────────────┘ └──────────────┘ └────────────────┘
```

<br>

<img src="https://img.shields.io/badge/LangGraph-1.0-8b5cf6?style=for-the-badge&logo=python&logoColor=white" alt="LangGraph"/>
<img src="https://img.shields.io/badge/LangChain-1.0-2dd4bf?style=for-the-badge&logo=chainlink&logoColor=white" alt="LangChain"/>
<img src="https://img.shields.io/badge/Langfuse-Tracing-f97316?style=for-the-badge&logo=opentelemetry&logoColor=white" alt="Langfuse"/>
<img src="https://img.shields.io/badge/Python-3.11+-3776ab?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>

<br>

[Demo Interativa](docs/demo.html) · [Como Funciona](#como-funciona) · [Quick Start](#quick-start) · [Arquitetura](#arquitetura)

</div>

---

## O que é isso?

Um sistema multi-agent onde um **Supervisor central** (LLM poderoso) recebe queries do usuário e **delega** a agentes especializados, cada um com suas ferramentas. O supervisor decide quem faz o quê, coleta os resultados e sintetiza uma resposta final.

> *"Pesquise o PIB do Brasil e calcule 15% dele"*
>
> O supervisor detecta dois domínios (pesquisa + math), delega ao Pesquisador, recebe o dado, delega ao Matemático, recebe o cálculo, e responde com tudo integrado.

## Demo Interativa

Abra o arquivo [`docs/demo.html`](docs/demo.html) no navegador para ver uma simulação animada do fluxo de execução do Supervisor — com partículas mostrando as mensagens entre agentes e um trace de execução em tempo real.

<div align="center">
<br>

```
╔══════════════════════════════════════════════════════════╗
║  [USR] "Pesquise o PIB do Brasil e calcule 15%"         ║
║  [SUP] Analisando... 2 domínios detectados              ║
║  [SUP] Delegando → research_expert                      ║
║  [WRK] web_search("PIB Brasil") → R$ 11.02 tri          ║
║  [SUP] Delegando → math_expert                          ║
║  [WRK] calculator("11.02e12 * 0.15") → R$ 1.653 tri     ║
║  [SUP] Sintetizando resposta final...                   ║
║  [RES] "O PIB é R$ 11,02 tri. 15% = R$ 1,653 tri."      ║
╚══════════════════════════════════════════════════════════╝
```

<br>
</div>

## Como Funciona

O padrão Supervisor funciona como um **hub-and-spoke**: toda comunicação passa pelo centro.

```
Usuário ──→ Supervisor ──→ Worker A ──→ resultado
                │                          │
                ├──────────────────────────←┘
                │
                ├──→ Worker B ──→ resultado
                │                     │
                ├────────────────────←┘
                │
                └──→ Resposta Final ──→ Usuário
```

O supervisor é um LLM (Mistral Large) com acesso a "ferramentas de delegação" — cada worker é registrado como uma tool. Ele analisa a query, escolhe o worker certo, envia a subtarefa, recebe o resultado, e decide se precisa delegar de novo ou se já pode responder.

### 1. Configure as variáveis de ambiente

```bash
cp .env.example .env
# Edite .env com suas chaves:
#   MISTRAL_API_KEY=...
#   LANGFUSE_PUBLIC_KEY=pk-lf-...
#   LANGFUSE_SECRET_KEY=sk-lf-...
```

### 2. Rode

```python
from src.supervisor import build_supervisor

app = build_supervisor()
result = app.invoke({
    "messages": [("user", "Pesquise quem ganhou a Copa de 2022 e escreva um resumo")]
})
print(result["messages"][-1].content)
```

## Arquitetura

```
┌──────────────────────────────────────────────┐
│                 SUPERVISOR                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Analisa  │→ │ Delega   │→ │ Sintetiza│   │
│  │ a query  │  │ ao worker│  │ resposta │   │
│  └──────────┘  └──────────┘  └──────────┘   │
└──────────┬────────────┬────────────┬─────────┘
           │            │            │
     ┌─────▼─────┐ ┌────▼────┐ ┌────▼────┐
     │ Research  │ │  Math   │ │ Writer  │
     │  Agent   │ │  Agent  │ │  Agent  │
     ├──────────┤ ├─────────┤ ├─────────┤
     │web_search│ │calculat.│ │generate │
     │fetch_url │ │plot     │ │summarize│
     └──────────┘ └─────────┘ └─────────┘
```

### Componentes

| Componente | Modelo | Papel |
|------------|--------|-------|
| **Supervisor** | `mistral-large-latest` | Analisa, delega, sintetiza |
| **Pesquisador** | `mistral-small-latest` | Busca informações na web |
| **Matemático** | `mistral-small-latest` | Cálculos e visualizações |
| **Escritor** | `mistral-small-latest` | Gera e resume textos |

### Observabilidade com Langfuse

Todas as chamadas são instrumentadas com Langfuse:

```
Trace: supervisor_invoke
├── Span: supervisor_decision (mistral-large-latest, 340 tokens)
├── Span: research_expert (mistral-small-latest, 280 tokens)
├── Span: supervisor_decision (mistral-large-latest, 190 tokens)
├── Span: math_expert (mistral-small-latest, 95 tokens)
└── Span: supervisor_synthesis (mistral-large-latest, 210 tokens)
     Total: 1,115 tokens | Latência: 4.2s | Custo: $0.008
```

## Estrutura do Projeto

```
supervisor-agent/
├── .claude/                    # Claude Code skills
│   ├── CLAUDE.md               # Contexto do projeto
│   ├── settings.json           # Permissões
│   └── skills/
│       ├── langgraph-supervisor.md
│       ├── langfuse-langgraph.md
│       └── langgraph-testing.md
├── src/
│   ├── config.py               # Configuração centralizada
│   ├── agents/                 # Definição dos workers
│   ├── tools/                  # Tools por domínio
│   └── supervisor.py           # Montagem do grafo
├── tests/
│   └── test_supervisor.py      # Testes unitários
├── docs/
│   └── demo.html               # Demo interativa
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml              # Ruff e metadados do projeto
└── README.md
```

## Roadmap

- [x] Setup do ambiente e dependências
- [ ] Definir tools dos worker agents
- [ ] Criar worker agents com `create_react_agent`
- [ ] Montar o grafo Supervisor e compilar
- [ ] Testes unitários
- [ ] Integração com Langfuse

## Conceitos-Chave

### O "Problema do Telefone" 📞

O supervisor parafraseia respostas dos workers ao devolver ao usuário — detalhes podem se perder. Mitigação: usar `create_forward_message_tool` para encaminhar respostas diretamente.

### output_mode

| Mode | Comportamento |
|------|---------------|
| `"full_history"` | Todo o histórico de mensagens propaga |
| `"last_message"` | Só a última mensagem do worker volta |

### Supervisor vs Swarm

O Supervisor centraliza o controle. O Swarm (implementado em outro projeto) distribui — cada agente fala direto com o usuário. Pros/cons:

| | Supervisor | Swarm |
|---|---|---|
| Execução paralela | ✅ | ❌ |
| Comunicação direta | ❌ | ✅ |
| Tokens | Mais | Menos |
| Agentes 3rd-party | ✅ | ❌ |

---

<div align="center">
<br>

**Built with LangGraph** · Parte do portfolio de estudos em Multi-Agent Systems

<br>
</div>
