"""Montagem e compilação do grafo Supervisor.

O supervisor é o orquestrador central que recebe queries do usuário,
delega a workers especializados e sintetiza a resposta final.
"""

from langchain_mistralai import ChatMistralAI
from langgraph_supervisor import create_supervisor

from src.agents.workers import build_all_workers
from src.config import SUPERVISOR_MODEL, SUPERVISOR_NAME


SUPERVISOR_PROMPT = (
    "Você é um supervisor que gerencia uma equipe de especialistas. "
    "Sua equipe possui:\n"
    "- research_expert: busca informações na web e extrai conteúdo de URLs\n"
    "- math_expert: realiza cálculos matemáticos, porcentagens e conversões de moeda\n"
    "- writer_expert: gera textos, resume conteúdo e formata em markdown\n\n"
    "Analise cada query do usuário e delegue ao especialista mais adequado. "
    "Se a query envolver múltiplos domínios, delegue sequencialmente — "
    "primeiro colete dados, depois processe, depois redija. "
    "Quando todos os dados necessários estiverem disponíveis, "
    "sintetize uma resposta completa e clara para o usuário. "
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
        prompt=SUPERVISOR_PROMPT,
        output_mode="full_history",
        supervisor_name=SUPERVISOR_NAME,
    )

    return workflow.compile()


def build_supervisor_with_langfuse():
    """Compat: retorna o grafo compilado. Tracing: ``langfuse_setup.invoke_supervisor_with_tracing``."""
    return build_supervisor()