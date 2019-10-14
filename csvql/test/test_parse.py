"""Test SQL parsing."""

# mypy: disallow-untyped-defs=False
# pylint: disable=missing-docstring

import unittest

from parse import parse

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
