"""LLM fake com fila de AIMessage e suporte a bind_tools (para testes com supervisor)."""

from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from typing_extensions import override


class QueuedAIMessageModel(BaseChatModel):
    """Consome uma fila de AIMessage na ordem; `bind_tools` retorna self."""

    responses: list[AIMessage]
    """Respostas em ordem de cada invoke do grafo (supervisor + workers)."""

    _i: int = 0

    @property
    @override
    def _llm_type(self) -> str:
        return "queued-ai-message"

    @override
    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        if self._i >= len(self.responses):
            msg = (
                f"QueuedAIMessageModel: fila esgotada (índice {self._i}, "
                f"tamanho {len(self.responses)})."
            )
            raise RuntimeError(msg)
        response = self.responses[self._i]
        self._i += 1
        return ChatResult(generations=[ChatGeneration(message=response)])

    def bind_tools(self, tools: Any, **kwargs: Any) -> BaseChatModel:
        return self

    @property
    @override
    def _identifying_params(self) -> dict[str, Any]:
        return {"n_queued": len(self.responses)}
