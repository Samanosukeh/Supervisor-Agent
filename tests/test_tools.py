"""Testes unitários para as tools (isoladas).

Cobertura supervisor + tools em cadeia: ``tests.test_supervisor`` (ex.: fluxo PIB scriptado)."""

import unittest

from src.tools.math_tools import calculator, convert_currency, percentage
from src.tools.research_tools import web_search
from src.tools.writer_tools import format_as_markdown, summarize


class TestCalculator(unittest.TestCase):
    """Testes para a tool calculator."""

    def test_basic_arithmetic(self):
        result = calculator.invoke({"expression": "2 + 3"})
        self.assertEqual(result, "5")

    def test_multiplication(self):
        result = calculator.invoke({"expression": "145 * 37"})
        self.assertEqual(result, "5365")

    def test_float_result(self):
        result = calculator.invoke({"expression": "10 / 3"})
        self.assertIn("3.33333", result)

    def test_scientific_notation(self):
        result = calculator.invoke({"expression": "11.02e12 * 0.15"})
        self.assertIn("1653", result)

    def test_math_functions(self):
        result = calculator.invoke({"expression": "sqrt(144)"})
        self.assertEqual(result, "12")

    def test_pi_constant(self):
        result = calculator.invoke({"expression": "pi"})
        self.assertIn("3.14159", result)

    def test_invalid_expression(self):
        result = calculator.invoke({"expression": "invalid_stuff"})
        self.assertIn("Erro", result)


class TestPercentage(unittest.TestCase):
    """Testes para a tool percentage."""

    def test_basic_percentage(self):
        result = percentage.invoke({"value": 1000.0, "percent": 15.0})
        self.assertIn("150", result)
        self.assertIn("%", result)
        self.assertIn("15", result)

    def test_zero_percentage(self):
        result = percentage.invoke({"value": 500.0, "percent": 0.0})
        self.assertIn("0", result)


class TestConvertCurrency(unittest.TestCase):
    """Testes para a tool convert_currency."""

    def test_brl_to_usd(self):
        result = convert_currency.invoke({
            "amount": 1000.0,
            "from_currency": "BRL",
            "to_currency": "USD",
        })
        self.assertIn("BRL", result)
        self.assertIn("USD", result)

    def test_unsupported_currency(self):
        result = convert_currency.invoke({
            "amount": 100.0,
            "from_currency": "XYZ",
            "to_currency": "USD",
        })
        self.assertIn("não suportada", result)


class TestWebSearch(unittest.TestCase):
    """Testes para a tool web_search (mock)."""

    def test_known_query_pib(self):
        result = web_search.invoke({"query": "PIB Brasil 2024"})
        self.assertIn("11,02 trilhões", result)

    def test_known_query_copa(self):
        result = web_search.invoke({"query": "Copa 2022 campeão"})
        self.assertIn("Argentina", result)

    def test_unknown_query_fallback(self):
        result = web_search.invoke({"query": "algo completamente aleatório"})
        self.assertIn("Resultados para", result)


class TestSummarize(unittest.TestCase):
    """Testes para a tool summarize."""

    def test_short_text_passthrough(self):
        text = "Uma frase curta."
        result = summarize.invoke({"text": text, "max_sentences": 3})
        self.assertEqual(result, text)

    def test_long_text_summary(self):
        text = "Primeira frase. Segunda frase. Terceira frase. Quarta frase. Quinta frase."
        result = summarize.invoke({"text": text, "max_sentences": 2})
        self.assertIn("Resumo solicitado", result)


class TestFormatAsMarkdown(unittest.TestCase):
    """Testes para a tool format_as_markdown."""

    def test_with_title(self):
        result = format_as_markdown.invoke({"content": "Conteúdo aqui", "title": "Meu Doc"})
        self.assertIn("# Meu Doc", result)

    def test_without_title(self):
        result = format_as_markdown.invoke({"content": "Conteúdo aqui", "title": ""})
        self.assertNotIn("#", result.split("\n")[0])


if __name__ == "__main__":
    unittest.main()
