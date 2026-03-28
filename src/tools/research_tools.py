"""Tools para o agente de pesquisa (research_expert).

Cada tool deve retornar string e ter docstring clara —
o supervisor usa a docstring para decidir delegação.
"""

from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """Busca informações atualizadas na web sobre qualquer tema.

    Use para encontrar dados recentes, notícias, fatos, estatísticas
    ou qualquer informação que precise de consulta externa.

    Args:
        query: Termo de busca descrevendo o que procurar.
    """
    # TODO: integrar com API real (Tavily, SerpAPI, etc.)
    # Por ora, retorna dados simulados para validar o fluxo
    mock_results = {
        "pib brasil": "O PIB do Brasil em 2024 foi de R$ 11,02 trilhões (US$ 2,2 trilhões), "
        "segundo o IBGE. Crescimento de 3,1% em relação a 2023.",
        "copa 2022": "A Argentina venceu a Copa do Mundo FIFA 2022 no Qatar, "
        "derrotando a França nos pênaltis por 4-2 após empate em 3-3. "
        "Lionel Messi foi eleito o melhor jogador do torneio.",
        "populacao mundo": "A população mundial em 2024 é de aproximadamente 8,1 bilhões "
        "de pessoas, segundo a ONU. China e Índia são os países mais populosos.",
    }

    query_lower = query.lower()
    for key, result in mock_results.items():
        if key in query_lower:
            return result

    return (
        f'Resultados para "{query}": Foram encontrados diversos artigos e fontes '
        f"relevantes sobre o tema. Informações disponíveis em fontes públicas e oficiais."
    )


@tool
def fetch_url(url: str) -> str:
    """Acessa e extrai o conteúdo textual de uma URL específica.

    Use quando precisar ler o conteúdo de uma página web específica,
    artigo, documentação ou qualquer recurso acessível por URL.

    Args:
        url: URL completa da página a ser acessada.
    """
    # TODO: integrar com requests/httpx real
    return (
        f"Conteúdo extraído de {url}: "
        f"[Conteúdo simulado da página — substituir por implementação real com requests/httpx]"
    )
