"""Utilitários Langfuse: cliente, callbacks LangChain e ``propagate_attributes``."""

from typing import Any

from langfuse import Langfuse, get_client, propagate_attributes
from langfuse.langchain import CallbackHandler

from src.config import LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY


def ensure_langfuse_client() -> None:
    """Regista o cliente singleton a partir do env antes de callbacks / ``get_client``."""
    if not is_langfuse_configured():
        return
    Langfuse()


def metadata_for_propagate(metadata: dict | None) -> dict[str, str] | None:
    """Converte metadata arbitrária para ``dict[str, str]`` (requisito do Langfuse OTel)."""
    if not metadata:
        return None
    out: dict[str, str] = {}
    for key, value in metadata.items():
        k = str(key)
        if len(k) > 200:
            k = k[:200]
        s = str(value)
        if len(s) > 200:
            s = s[:197] + "..."
        out[k] = s
    return out or None


def build_langfuse_run_config(
    session_id: str | None = None,
    user_id: str | None = None,
    tags: list[str] | None = None,
    metadata: dict | None = None,
    base_config: dict | None = None,
) -> dict:
    """Metadata + :class:`CallbackHandler` para ``app.stream`` / ``invoke``.

    O handler regista no Langfuse as chamadas LLM, tools e sub-cadeias LangChain
    dentro do grafo (detalhe que o ``@observe`` sozinho não cobre).
    """
    handler = CallbackHandler(public_key=LANGFUSE_PUBLIC_KEY or None)
    merged: dict = dict((base_config or {}).get("metadata") or {})
    if session_id:
        merged["langfuse_session_id"] = session_id
    if user_id:
        merged["langfuse_user_id"] = user_id
    merged["langfuse_tags"] = list(tags or ["supervisor-agent"])
    extra = metadata_for_propagate(metadata)
    if extra:
        merged.update(extra)
    return {"callbacks": [handler], "metadata": merged}


def merge_run_config(user: dict | None, langfuse: dict) -> dict[str, Any]:
    """Junta ``config`` do utilizador com o dict devolvido por :func:`build_langfuse_run_config`."""
    out: dict[str, Any] = dict(user or {})
    out["callbacks"] = list(out.get("callbacks") or []) + list(
        langfuse.get("callbacks") or []
    )
    um = dict(out.get("metadata") or {})
    lm = langfuse.get("metadata") or {}
    out["metadata"] = {**um, **lm}
    return out


def invoke_supervisor_with_tracing(
    app: Any,
    input_state: dict[str, Any],
    *,
    session_id: str | None = None,
    user_id: str | None = None,
    tags: list[str] | None = None,
    metadata: dict | None = None,
    config: dict | None = None,
) -> dict[str, Any]:
    """``app.invoke`` com Langfuse (callbacks LLM/tools + sessão no trace)."""
    ensure_langfuse_client()
    base = dict(config) if config else {}
    lf = build_langfuse_run_config(
        session_id=session_id,
        user_id=user_id,
        tags=tags,
        metadata=metadata,
        base_config=base,
    )
    merged = merge_run_config(base, lf)
    with propagate_attributes(
        session_id=session_id,
        user_id=user_id,
        tags=tags or ["supervisor-agent"],
        metadata=metadata_for_propagate(metadata),
        trace_name="supervisor-graph",
    ):
        result = app.invoke(input_state, config=merged)
    flush_langfuse_traces()
    return result


def is_langfuse_configured() -> bool:
    """True se as credenciais mínimas estiverem definidas (env)."""
    return bool(LANGFUSE_PUBLIC_KEY.strip() and LANGFUSE_SECRET_KEY.strip())


def flush_langfuse_traces() -> None:
    """Envia spans pendentes ao Langfuse.

    Usa ``get_client()`` sem ``public_key``: com um único projeto no processo,
    isso cria ou reutiliza o cliente carregado das variáveis de ambiente.
    Passar ``public_key`` antes de existir instância registada faz o SDK
    devolver cliente desativado e nada é exportado.
    """
    if not is_langfuse_configured():
        return
    get_client().flush()
