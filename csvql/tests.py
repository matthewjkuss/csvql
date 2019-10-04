"""Various unit tests."""

# mypy: disallow-untyped-defs=False
# pylint: disable=missing-docstring


import unittest

from tokenise import tokenise
from parse import parse


# "SELECT customer_name",
# "SELECT customer_name FROM customer;",
# "SELECT customer_name, id FROM customer;",
# "SELECT customer_name+ id FROM customer;",
# "SELECT DISTINCT customer_name FROM customer;"


class Tokenise(unittest.TestCase):
    def test_empty(self):
        self.assertEqual([], tokenise("").value)

    def test_word(self):
        self.assertEqual([("word", "hello")], tokenise("hello").value)

    def test_words(self):
        self.assertEqual([("word", "hello"), ("word", "world")],
                         tokenise("hello world").value)

    def test_single_digit(self):
        self.assertEqual([("number", "7")], tokenise("7").value)

    def test_multiple_digit(self):
        self.assertEqual([("number", "010")], tokenise("010").value)

    def test_keyword(self):
        self.assertEqual([("keyword", "select")], tokenise("select").value)

    def test_empty_word(self):
        self.assertEqual(tokenise("\"\"").value, [("word", "")])

    def test_quote_character(self):
        for quote in ("\"", "\'"):
            self.assertEqual(
                tokenise(f"{quote}{quote}{quote}{quote}").value,
                [("word", f"{quote}")]
            )

    def test_quoted_keyword(self):
        self.assertEqual([("word", "select")], tokenise("\"select\"").value)

    def test_quoted_word(self):
        self.assertEqual([("word", "hello")], tokenise("\"hello\"").value)

    def test_quoted_phrase(self):
        self.assertEqual([("word", "Hello, world!")],
                         tokenise("\"Hello, world!\"").value)

    def test_list_of_quotes(self):
        self.assertEqual(tokenise("\"foo\",\"bar\"").value, [
            ("word", "foo"),
            ("operator", ","),
            ("word", "bar")
        ])

    def test_sum(self):
        self.assertEqual([("number", "2"), ("operator", "+"),
                          ("number", "2")], tokenise("2+2").value)

    def test_select(self):
        self.assertEqual(
            tokenise(
                "select customer, street1, \"limit\", 'addr''s' FROM Table").value,
            [
                ("keyword", "select"),
                ("word", "customer"),
                ("operator", ","),
                ("word", "street1"),
                ("operator", ","),
                ("word", "limit"),
                ("operator", ","),
                ("word", "addr's"),
                ("keyword", "from"),
                ("word", "Table")
            ])


class Parse(unittest.TestCase):
    def test_empty(self):
        self.assertIn("Error: No tokens to consume.", parse("").messages)

    def test_maths_expr(self):
        self.assertIn("Error: Expected keyword, but got `2`.",
                      parse("2+2").messages)

    def test_word(self):
        self.assertIn("Error: Expected keyword, but got `hi`.",
                      parse("hi").messages)

    def test_phrase(self):
        self.assertIn("Error: Expected keyword, but got `hello`.",
                      parse("hello world").messages)

    def test_floating_flag(self):
        self.assertIn("Error: Keyword `distinct` is not a valid clause name.", parse(
            "distinct").messages)

    def test_nonprimary_clause(self):
        self.assertIn("Error: Clause `where` is not primary.",
                      parse("where").messages)

    def test_invalid_prefix(self):
        self.assertIn("Error: Keyword `asc` is not a valid prefix for `select`.", parse(
            "asc select").messages)


if __name__ == "__main__":
    unittest.main()
