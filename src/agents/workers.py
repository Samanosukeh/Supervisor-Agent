"""Worker agents especializados para o Supervisor.

Cada agent é criado com langchain.agents.create_agent e recebe:
- Um modelo LLM (mistral-small-latest para workers)
- Um conjunto de tools do seu domínio
- Um name único (constante importada de config)
- Um system_prompt descrevendo sua especialização
"""

from langchain.agents import create_agent
from langchain_mistralai import ChatMistralAI

from src.config import (
    MATH_AGENT,
    RESEARCH_AGENT,
    WORKER_MODEL,
    WRITER_AGENT,
)
from src.tools import MATH_TOOLS, RESEARCH_TOOLS, WRITER_TOOLS


def _build_worker_model() -> ChatMistralAI:
    """Instancia o modelo compartilhado por todos os workers."""
    return ChatMistralAI(model=WORKER_MODEL)


def build_research_agent():
    """Cria o agente especializado em pesquisa."""
    return create_agent(
        _build_worker_model(),
        tools=RESEARCH_TOOLS,
        name=RESEARCH_AGENT,
        system_prompt=(
            "Você é um especialista em pesquisa e coleta de informações. "
            "Use suas ferramentas para buscar dados atualizados na web, "
            "extrair conteúdo de URLs e compilar informações relevantes. "
            "Sempre cite a fonte dos dados encontrados. "
            "Responda em português brasileiro."
        ),
    )


def build_math_agent():
    """Cria o agente especializado em matemática e cálculos."""
    return create_agent(
        _build_worker_model(),
        tools=MATH_TOOLS,
        name=MATH_AGENT,
        system_prompt=(
            "Você é um especialista em matemática, cálculos e conversões numéricas. "
            "Use suas ferramentas para avaliar expressões, calcular porcentagens "
            "e converter entre moedas. Sempre mostre a conta realizada. "
            "Responda em português brasileiro."
        ),
    )


def build_writer_agent():
    """Cria o agente especializado em escrita e produção de conteúdo."""
    return create_agent(
        _build_worker_model(),
        tools=WRITER_TOOLS,
        name=WRITER_AGENT,
        system_prompt=(
            "Você é um especialista em redação e produção de conteúdo. "
            "Use suas ferramentas para gerar textos, resumir informações "
            "e formatar conteúdo em markdown estruturado. "
            "Produza textos claros, bem organizados e em português brasileiro."
        ),
    )


def build_all_workers() -> list:
    """Constrói e retorna todos os worker agents."""
    return [
        build_research_agent(),
        build_math_agent(),
        build_writer_agent(),
    ]
