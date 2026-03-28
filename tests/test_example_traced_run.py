"""Demo do supervisor com Langfuse opcional (prints por iteração com ``subTest``).

Rode com: ``python -m unittest tests.test_example_traced_run -v``
Requer: ``MISTRAL_API_KEY`` no ``.env``. Langfuse: opcional (``LANGFUSE_*``).
"""

import unittest
import warnings

from src.config import MISTRAL_API_KEY
from src.observability.langfuse_setup import (
    invoke_supervisor_with_tracing,
    is_langfuse_configured,
)
from src.supervisor import build_supervisor


def setUpModule():
    from langgraph.warnings import LangGraphDeprecatedSinceV10

    warnings.filterwarnings("ignore", category=LangGraphDeprecatedSinceV10)


@unittest.skipUnless(
    MISTRAL_API_KEY.strip(),
    "MISTRAL_API_KEY ausente — defina no .env",
)
class TestExampleTracedRun(unittest.TestCase):
    """Três queries com saída no console (comportamento do antigo ``example_traced_run``)."""

    def test_demo_queries(self):
        app = build_supervisor()

        queries = [
            "Pesquise o PIB do Brasil e calcule 15% dele",
            "Quanto é 1450 * 37 + 892?",
            "Pesquise quem ganhou a Copa 2022 e escreva um resumo",
        ]

        for i, query in enumerate(queries, 1):
            with self.subTest(query_index=i, query=query):
                print(f"\n{'='*60}")
                print(f"QUERY {i}: {query}")
                print("=" * 60)

                if is_langfuse_configured():
                    result = invoke_supervisor_with_tracing(
                        app,
                        {"messages": [("user", query)]},
                        session_id="demo-session",
                        user_id="dev-local",
                        tags=["supervisor", "demo"],
                        metadata={
                            "query_index": i,
                            "architecture": "supervisor",
                        },
                    )
                    print("✓ Trace enviado ao Langfuse (flush no fim de cada invoke)")
                else:
                    result = app.invoke({"messages": [("user", query)]})
                    print("(LANGFUSE_* ausente — invoke sem tracing)")

                print(f"\nRESPOSTA: {result['messages'][-1].content}")
                print(f"Mensagens no histórico: {len(result['messages'])}")



if __name__ == "__main__":
    unittest.main()
