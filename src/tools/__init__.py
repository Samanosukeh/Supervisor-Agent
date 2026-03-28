"""Tools organizadas por domínio para os worker agents."""

from src.tools.math_tools import calculator, convert_currency, percentage
from src.tools.research_tools import fetch_url, web_search
from src.tools.writer_tools import format_as_markdown, generate_text, summarize

# Agrupados por domínio — facilita montar os agents
RESEARCH_TOOLS = [web_search, fetch_url]
MATH_TOOLS = [calculator, percentage, convert_currency]
WRITER_TOOLS = [generate_text, summarize, format_as_markdown]

__all__ = [
    "web_search",
    "fetch_url",
    "calculator",
    "percentage",
    "convert_currency",
    "generate_text",
    "summarize",
    "format_as_markdown",
    "RESEARCH_TOOLS",
    "MATH_TOOLS",
    "WRITER_TOOLS",
]
