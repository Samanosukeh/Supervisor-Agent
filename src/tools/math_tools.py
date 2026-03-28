"""Tools para o agente de matemática (math_expert).

Inclui cálculos, conversões e formatação numérica.
"""

import math

from langchain_core.tools import tool


@tool
def calculator(expression: str) -> str:
    """Avalia expressões matemáticas e retorna o resultado.

    Suporta operações básicas (+, -, *, /, **), funções matemáticas
    (sqrt, sin, cos, log, etc.) e constantes (pi, e).

    Args:
        expression: Expressão matemática a ser calculada.
                    Exemplos: "145 * 37", "sqrt(144)", "11.02e12 * 0.15"
    """
    allowed_names = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "log10": math.log10,
        "log2": math.log2,
        "abs": abs,
        "round": round,
        "pow": pow,
        "pi": math.pi,
        "e": math.e,
        "inf": math.inf,
    }

    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)  # noqa: S307
        if isinstance(result, float):
            if result == int(result) and not math.isinf(result):
                return str(int(result))
            return f"{result:,.6f}".rstrip("0").rstrip(",")
        return str(result)
    except Exception as exc:
        return f"Erro ao calcular '{expression}': {exc}"


@tool
def percentage(value: float, percent: float) -> str:
    """Calcula a porcentagem de um valor.

    Args:
        value: Valor base.
        percent: Porcentagem desejada (ex: 15 para 15%).
    """
    result = value * (percent / 100)
    return f"{percent}% de {value:,.2f} = {result:,.2f}"


@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Converte valores entre moedas usando taxas aproximadas.

    Args:
        amount: Valor a converter.
        from_currency: Moeda de origem (ex: "BRL", "USD", "EUR").
        to_currency: Moeda de destino (ex: "USD", "BRL", "EUR").
    """
    # Taxas aproximadas (fixas para mock — substituir por API real)
    rates_to_usd = {
        "USD": 1.0,
        "BRL": 0.18,
        "EUR": 1.08,
        "GBP": 1.27,
        "JPY": 0.0067,
    }

    from_c = from_currency.upper()
    to_c = to_currency.upper()

    if from_c not in rates_to_usd or to_c not in rates_to_usd:
        return f"Moeda não suportada. Disponíveis: {', '.join(rates_to_usd.keys())}"

    usd_amount = amount * rates_to_usd[from_c]
    result = usd_amount / rates_to_usd[to_c]

    return f"{amount:,.2f} {from_c} = {result:,.2f} {to_c} (taxa aproximada)"
