"""Montagem e compilação do grafo Supervisor.

O supervisor é o orquestrador central que recebe queries do usuário,
delega a workers especializados e sintetiza a resposta final.
"""

from langchain_mistralai import ChatMistralAI
from langgraph_supervisor import create_forward_message_tool, create_supervisor

from src.agents.workers import build_all_workers
from src.config import (
    MATH_AGENT,
    RESEARCH_AGENT,
    SUPERVISOR_MODEL,
    SUPERVISOR_NAME,
    WRITER_AGENT,
)


SUPERVISOR_PROMPT = (
    "Você é um supervisor que gerencia uma equipe de especialistas. "
    "Sua equipe possui:\n"
    f"- {RESEARCH_AGENT}: busca informações na web e extrai conteúdo de URLs\n"
    f"- {MATH_AGENT}: realiza cálculos matemáticos, porcentagens e conversões de moeda\n"
    f"- {WRITER_AGENT}: gera textos, resume conteúdo e formata em markdown\n\n"
    "Analise cada query do usuário e delegue ao especialista mais adequado. "
    "Se a query envolver múltiplos domínios, delegue sequencialmente — "
    "primeiro colete dados, depois processe, depois redija. "
    "Quando a resposta de um especialista já for adequada para o usuário (números, "
    "citações ou texto final), use a ferramenta forward_message com o parâmetro "
    "from_agent igual ao nome desse especialista para encaminhar a mensagem sem "
    "reformular — evita perda de detalhes (telefone sem fio). "
    "Se precisar combinar ou sintetizar várias fontes, responda em texto próprio. "
    "Responda sempre em português brasileiro."
)


def build_supervisor():
    """Constrói e compila o grafo supervisor com todos os workers.

    Returns:
        CompiledGraph pronto para invocar com app.invoke({"messages": [...]})
    """
    supervisor_model = ChatMistralAI(model=SUPERVISOR_MODEL)
    workers = build_all_workers()

    workflow = create_supervisor(
        agents=workers,
        model=supervisor_model,
        tools=[create_forward_message_tool(supervisor_name=SUPERVISOR_NAME)],
        prompt=SUPERVISOR_PROMPT,
        output_mode="full_history",
        supervisor_name=SUPERVISOR_NAME,
    )

    return workflow.compile()


def build_supervisor_with_langfuse():
    """Compat: retorna o grafo compilado. Tracing: ``langfuse_setup.invoke_supervisor_with_tracing``."""
    return build_supervisor()