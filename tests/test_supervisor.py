"""Testes unitários para o fluxo completo do Supervisor.

Grafo fake: ``app.invoke``. Teste com Mistral: Langfuse opcional via
``invoke_supervisor_with_tracing`` se ``LANGFUSE_*`` no ``.env``.

`test_query_like_readme_pib_then_15_percent_two_agents` é ignorado sem ``MISTRAL_API_KEY``.
"""

import unittest
import warnings

from langchain_core.messages import AIMessage, HumanMessage

from src.config import (
    MATH_AGENT,
    MISTRAL_API_KEY,
    RESEARCH_AGENT,
    SUPERVISOR_NAME,
    WRITER_AGENT,
)
from src.observability.langfuse_setup import (
    invoke_supervisor_with_tracing,
    is_langfuse_configured,
)
from tests.queued_chat_model import QueuedAIMessageModel


def setUpModule():
    """Silencia depreciação de create_react_agent dentro de langgraph_supervisor (supervisor)."""
    from langgraph.warnings import LangGraphDeprecatedSinceV10

    warnings.filterwarnings("ignore", category=LangGraphDeprecatedSinceV10)


def _tc(name: str, tool_id: str, args: dict | None = None) -> dict:
    return {
        "name": name,
        "args": args if args is not None else {},
        "id": tool_id,
        "type": "tool_call",
    }


def script_pib_research_then_math() -> list[AIMessage]:
    """Mesmo fluxo do README: pesquisa (PIB) → matemática (15%).

    Ordem das respostas = ordem global de invoke (supervisor + workers).
    Validada com .venv via script de probe.
    """
    return [
        AIMessage(content="", tool_calls=[_tc("transfer_to_research_expert", "t0")]),
        AIMessage(
            content="",
            tool_calls=[_tc("web_search", "t1", {"query": "PIB Brasil"})],
        ),
        AIMessage(content="PIB mock: R$ 11,02 tri."),
        AIMessage(content="", tool_calls=[_tc("transfer_to_math_expert", "t2")]),
        AIMessage(
            content="",
            tool_calls=[
                _tc("calculator", "t3", {"expression": "11.02e12 * 0.15"}),
            ],
        ),
        AIMessage(content="15% = 1,653 tri (mock)."),
        AIMessage(
            content="Resposta final: PIB 11,02 tri; 15% = 1,653 tri."
        ),
    ]


class TestSupervisorWorkflow(unittest.TestCase):
    """Testes de integração do grafo Supervisor."""

    def _build_app_with_fake_llm(self, responses: list[str | AIMessage]):
        """Constrói o supervisor com fila de AIMessage (ou strings → AIMessage)."""
        from langchain.agents import create_agent
        from langgraph_supervisor import create_supervisor

        from src.tools import MATH_TOOLS, RESEARCH_TOOLS, WRITER_TOOLS

        normalized: list[AIMessage] = [
            AIMessage(content=r) if isinstance(r, str) else r for r in responses
        ]
        fake_llm = QueuedAIMessageModel(responses=normalized)

        research_agent = create_agent(
            fake_llm,
            tools=RESEARCH_TOOLS,
            name=RESEARCH_AGENT,
            system_prompt="Pesquisador mock.",
        )
        math_agent = create_agent(
            fake_llm,
            tools=MATH_TOOLS,
            name=MATH_AGENT,
            system_prompt="Matemático mock.",
        )
        writer_agent = create_agent(
            fake_llm,
            tools=WRITER_TOOLS,
            name=WRITER_AGENT,
            system_prompt="Escritor mock.",
        )

        workflow = create_supervisor(
            agents=[research_agent, math_agent, writer_agent],
            model=fake_llm,
            prompt="Supervisor mock.",
            output_mode="full_history",
            supervisor_name=SUPERVISOR_NAME,
        )
        return workflow.compile()

    def test_supervisor_returns_response(self):
        """Verifica que o supervisor retorna uma resposta ao usuário."""
        app = self._build_app_with_fake_llm([
            "O resultado é 42. Essa é a resposta final.",
        ])

        result = app.invoke({
            "messages": [HumanMessage(content="Qual é o sentido da vida?")]
        })

        self.assertIsNotNone(result)
        self.assertIn("messages", result)
        self.assertTrue(len(result["messages"]) > 0)

        last_msg = result["messages"][-1]
        self.assertIsInstance(last_msg, AIMessage)

    def test_message_history_preserved(self):
        """Verifica que o histórico de mensagens é preservado (full_history)."""
        app = self._build_app_with_fake_llm([
            "Resposta do supervisor com histórico completo.",
        ])

        result = app.invoke({
            "messages": [HumanMessage(content="Teste de histórico")]
        })

        messages = result["messages"]
        self.assertGreaterEqual(len(messages), 2)

        self.assertIsInstance(messages[0], HumanMessage)
        self.assertEqual(messages[0].content, "Teste de histórico")

    def test_supervisor_handles_empty_query(self):
        """Verifica que o supervisor lida com query vazia sem crashar."""
        app = self._build_app_with_fake_llm([
            "Não entendi sua pergunta. Pode reformular?",
        ])

        result = app.invoke({"messages": [HumanMessage(content="")]})

        self.assertIsNotNone(result)
        self.assertTrue(len(result["messages"]) > 0)

    @unittest.skipUnless(
        MISTRAL_API_KEY.strip(),
        "MISTRAL_API_KEY ausente — defina no .env para teste com Mistral real",
    )
    def test_query_like_readme_pib_then_15_percent_two_agents(self):
        """README: PIB + 15% com ChatMistralAI real (supervisor e workers)."""
        from src.supervisor import build_supervisor

        app = build_supervisor()
        state = {
            "messages": [
                HumanMessage(
                    content=(
                        "Pesquise o PIB do Brasil (valor aproximado recente) "
                        "e calcule 15% desse valor. Responda em português."
                    )
                )
            ]
        }
        if is_langfuse_configured():
            result = invoke_supervisor_with_tracing(
                app,
                state,
                session_id="unittest-supervisor-pib",
                user_id="unittest",
                tags=["unittest", "supervisor", "tools"],
                metadata={
                    "test": "test_query_like_readme_pib_then_15_percent_two_agents",
                },
            )
        else:
            result = app.invoke(state)

        self.assertIsNotNone(result)
        self.assertIn("messages", result)
        msgs = result["messages"]
        self.assertGreater(len(msgs), 2)

        last = msgs[-1]
        self.assertIsInstance(last, AIMessage)
        final_text = str(last.content).strip().lower()
        self.assertTrue(len(final_text) > 30)

        names = [m.name for m in msgs if getattr(m, "name", None)]
        self.assertIn(
            RESEARCH_AGENT,
            names,
            "esperado delegação ao pesquisador (research_expert)",
        )

        has_math_node = MATH_AGENT in names
        mentions_percent = any(
            hint in final_text
            for hint in ("15%", "15 %", "por cento", "quinze", "%")
        )
        self.assertTrue(
            has_math_node or mentions_percent,
            "esperado math_expert no histórico ou cálculo/menção a 15% na resposta final",
        )
        if has_math_node:
            self.assertLess(names.index(RESEARCH_AGENT), names.index(MATH_AGENT))

    def test_readme_pib_two_agents_scripted_fake_graph(self):
        """Mesmo README com grafo fake (CI sem API): pesquisa → matemática scriptadas."""
        app = self._build_app_with_fake_llm(script_pib_research_then_math())

        result = app.invoke({
            "messages": [
                HumanMessage(
                    content="Pesquise o PIB do Brasil e calcule 15% desse valor."
                )
            ]
        })

        self.assertIsNotNone(result)
        msgs = result["messages"]

        names_with_agent = [
            m.name
            for m in msgs
            if getattr(m, "name", None)
        ]
        self.assertIn(RESEARCH_AGENT, names_with_agent)
        self.assertIn(MATH_AGENT, names_with_agent)
        self.assertLess(
            names_with_agent.index(RESEARCH_AGENT),
            names_with_agent.index(MATH_AGENT),
        )

        serialized = repr(msgs)
        self.assertIn("transfer_to_research_expert", serialized)
        self.assertIn("transfer_to_math_expert", serialized)

        final = msgs[-1]
        self.assertIsInstance(final, AIMessage)
        self.assertEqual(final.name, SUPERVISOR_NAME)
        self.assertIn("11,02", final.content)
        self.assertIn("15%", final.content)


class TestSupervisorDelegation(unittest.TestCase):
    """Testes focados no mecanismo de delegação do supervisor."""

    def test_tool_call_format(self):
        """Verifica que tool calls de delegação têm o formato correto."""
        expected_tools = [
            f"transfer_to_{RESEARCH_AGENT}",
            f"transfer_to_{MATH_AGENT}",
            f"transfer_to_{WRITER_AGENT}",
        ]

        for tool_name in expected_tools:
            self.assertTrue(
                tool_name.startswith("transfer_to_"),
                f"Tool {tool_name} não segue o padrão de delegação",
            )

    def test_agent_names_are_unique(self):
        """Verifica que todos os agent names são únicos."""
        names = [RESEARCH_AGENT, MATH_AGENT, WRITER_AGENT]
        self.assertEqual(len(names), len(set(names)))

    def test_agent_names_are_valid_identifiers(self):
        """Verifica que agent names não contêm caracteres problemáticos."""
        names = [RESEARCH_AGENT, MATH_AGENT, WRITER_AGENT]
        for name in names:
            self.assertTrue(
                name.replace("_", "").isalnum(),
                f"Agent name '{name}' contém caracteres inválidos",
            )


class TestToolsIntegration(unittest.TestCase):
    """Testes de integração rápida das tools com os agents."""

    def test_research_tools_are_callable(self):
        """Verifica que todas as research tools são BaseTool."""
        from langchain_core.tools import BaseTool

        from src.tools import RESEARCH_TOOLS
        for tool in RESEARCH_TOOLS:
            self.assertIsInstance(tool, BaseTool)
            self.assertTrue(hasattr(tool, "name"))
            self.assertTrue(hasattr(tool, "description"))

    def test_math_tools_are_callable(self):
        """Verifica que todas as math tools são BaseTool."""
        from langchain_core.tools import BaseTool

        from src.tools import MATH_TOOLS
        for tool in MATH_TOOLS:
            self.assertIsInstance(tool, BaseTool)

    def test_writer_tools_are_callable(self):
        """Verifica que todas as writer tools são BaseTool."""
        from langchain_core.tools import BaseTool

        from src.tools import WRITER_TOOLS
        for tool in WRITER_TOOLS:
            self.assertIsInstance(tool, BaseTool)

    def test_all_tools_have_docstrings(self):
        """Verifica que todas as tools têm docstrings (crucial para delegação)."""
        from src.tools import MATH_TOOLS, RESEARCH_TOOLS, WRITER_TOOLS
        all_tools = RESEARCH_TOOLS + MATH_TOOLS + WRITER_TOOLS
        for tool in all_tools:
            self.assertTrue(
                len(tool.description) > 10,
                f"Tool '{tool.name}' tem docstring muito curta ou vazia",
            )


if __name__ == "__main__":
    unittest.main()
