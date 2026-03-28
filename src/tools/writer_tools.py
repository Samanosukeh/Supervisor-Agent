"""Tools para o agente de escrita (writer_expert).

Geração de texto, resumos e formatação de conteúdo.
"""

from langchain_core.tools import tool


@tool
def generate_text(topic: str, style: str = "informativo", max_words: int = 200) -> str:
    """Gera texto sobre um tema no estilo especificado.

    Use para criar conteúdo original: artigos, posts, descrições,
    explicações ou qualquer texto estruturado.

    Args:
        topic: Tema ou assunto do texto a ser gerado.
        style: Estilo do texto — "informativo", "casual", "formal", "técnico".
        max_words: Limite aproximado de palavras (padrão: 200).
    """
    # Nota: na prática, o próprio LLM do agente gera o texto.
    # Esta tool existe para dar estrutura à delegação e registrar
    # a intenção no trace do Langfuse.
    return (
        f"[Texto gerado]\n"
        f"Tema: {topic}\n"
        f"Estilo: {style}\n"
        f"Limite: ~{max_words} palavras\n\n"
        f"O agente escritor irá elaborar o conteúdo completo sobre '{topic}' "
        f"utilizando o estilo {style}, respeitando o limite de {max_words} palavras."
    )


@tool
def summarize(text: str, max_sentences: int = 3) -> str:
    """Resume um texto longo em poucas sentenças.

    Use para condensar informações, criar abstracts ou
    extrair os pontos principais de um texto extenso.

    Args:
        text: Texto a ser resumido.
        max_sentences: Número máximo de sentenças no resumo (padrão: 3).
    """
    # Nota: o LLM faz o resumo real. A tool estrutura o pedido.
    sentences = text.split(". ")
    if len(sentences) <= max_sentences:
        return text

    preview = ". ".join(sentences[:max_sentences]) + "."
    return (
        f"[Resumo solicitado: {max_sentences} sentenças]\n"
        f"Texto original: {len(sentences)} sentenças, ~{len(text.split())} palavras.\n"
        f"Preview: {preview}\n\n"
        f"O agente escritor irá produzir um resumo conciso."
    )


@tool
def format_as_markdown(content: str, title: str = "") -> str:
    """Formata conteúdo como Markdown estruturado com headers e listas.

    Use para organizar informações brutas em um documento
    bem formatado e legível.

    Args:
        content: Conteúdo bruto a ser formatado.
        title: Título opcional para o documento.
    """
    header = f"# {title}\n\n" if title else ""
    return (
        f"{header}"
        f"{content}\n\n"
        f"---\n"
        f"*Documento formatado pelo writer_expert*"
    )
