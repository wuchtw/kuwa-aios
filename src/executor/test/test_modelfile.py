import unittest
import logging
from kuwa.executor.modelfile import extract_text_from_quotes, discard_comments, Script


class TestExtractTextFromQuotes(unittest.TestCase):
    test_cases = {
        '"This is a text"': "This is a text",
        '"It\'s a text"': "It's a text",
        '"""multi-line\ntext"""': "multi-line\ntext",
        '"it\'s a text"': "it's a text",
        "'Made with \"love\"'": 'Made with "love"',
        '"""multi-line\ntext\nMade with "love""""': 'multi-line\ntext\nMade with "love"',
        '"""multi-line\ntext\nMade with \'love\'"""': "multi-line\ntext\nMade with 'love'",
        "'He said, \"Hello!\"'": 'He said, "Hello!"',
        "\"She replied, 'Hi there!'\"": "She replied, 'Hi there!'",
        "No quotes here": "No quotes here",
        "Invalid 'syntax'": "Invalid 'syntax'",
        " No quote with spaces  ": "No quote with spaces",
        ' "Quote with space "   ': "Quote with space ",
        " 'Quote with space '   ": "Quote with space ",
        ' """Quote with new line and space\n """   ': "Quote with new line and space\n ",
    }

    def test(self):
        for test_case, correct_result in self.test_cases.items():
            result = extract_text_from_quotes(test_case)
            self.assertEqual(result, correct_result)


class TestScriptSyntax(unittest.TestCase):
    test_cases = {
        Script.DEFAULT: (True, Script.DEFAULT_CONTENT),
        "000IPO": (True, "IPO"),
        "000": (True, ""),
        " 000 ": (True, ""),
        "000;;;": (True, ";;;"),
        "000OPIII": (True, "OPIII"),
        "000I[PO]": (True, "I[PO]"),
        "123": (False, None),
        "123IPO": (False, None),
        "IPO": (False, None),
        " 1213": (False, None),
        "": (False, None),
    }

    def test(self):
        for test_case, correct_result in self.test_cases.items():
            result = (Script.validate_syntax(test_case), Script.get_content(test_case))
            self.assertEqual(result, correct_result)


class TestDiscardComments(unittest.TestCase):
    def test_example_case(self):
        # Example provided in the problem description
        input_string = '123"[##:##:## -> ##:##:#]" #comment'
        expected_output = '123"[##:##:## -> ##:##:#]"'
        self.assertEqual(discard_comments(input_string), expected_output)

    def test_no_comments(self):
        # String with no comments
        input_string = "This is a string without any comments."
        expected_output = "This is a string without any comments."
        self.assertEqual(discard_comments(input_string), expected_output)

    def test_simple_comment_at_end(self):
        # Simple comment at the end of the string
        input_string = "Hello World! # This is a comment."
        expected_output = "Hello World!"
        self.assertEqual(discard_comments(input_string), expected_output)

    def test_full_line_comment(self):
        # Entire string is a comment
        input_string = "# This is a full line comment"
        expected_output = ""
        self.assertEqual(discard_comments(input_string), expected_output)

    def test_empty_string(self):
        # Empty input string
        input_string = ""
        expected_output = ""
        self.assertEqual(discard_comments(input_string), expected_output)

    def test_hash_inside_double_quotes(self):
        # Hash symbol inside double quotes
        input_string = 'My string contains a "#" symbol.'
        expected_output = 'My string contains a "#" symbol.'
        self.assertEqual(discard_comments(input_string), expected_output)

    def test_hash_inside_single_quotes(self):
        # Hash symbol inside single quotes
        input_string = "My string contains a '#' symbol."
        expected_output = "My string contains a '#' symbol."
        self.assertEqual(discard_comments(input_string), expected_output)

    def test_hash_inside_quotes_then_comment(self):
        # Hash inside quotes followed by a real comment
        input_string = 'Value is "#abc" # actual comment'
        expected_output = 'Value is "#abc"'
        self.assertEqual(discard_comments(input_string), expected_output)

    def test_multiple_quotes_and_comments(self):
        # More complex scenario with multiple quotes and comments
        input_string = 'data = \'{"key": "value#withhash"}\' # comment after json'
        expected_output = 'data = \'{"key": "value#withhash"}\''
        self.assertEqual(discard_comments(input_string), expected_output)

    def test_comment_immediately_after_string(self):
        # Comment immediately after a string literal
        input_string = '"quoted string"#comment'
        expected_output = '"quoted string"'
        self.assertEqual(discard_comments(input_string), expected_output)

    def test_single_and_double_quotes_interleaved_no_comment(self):
        # Interleaved quotes without comments
        input_string = "text with 'single' and \"double\" quotes"
        expected_output = "text with 'single' and \"double\" quotes"
        self.assertEqual(discard_comments(input_string), expected_output)

    def test_single_and_double_quotes_interleaved_with_comment(self):
        # Interleaved quotes with a comment
        input_string = "text with 'single' and \"double\" quotes # a comment"
        expected_output = "text with 'single' and \"double\" quotes"
        self.assertEqual(discard_comments(input_string), expected_output)

    def test_hash_at_beginning_of_line_after_string(self):
        # Test case where a hash is at the very beginning of the string,
        # but after some content.
        input_string = "some_var = 123# This is a comment"
        expected_output = "some_var = 123"
        self.assertEqual(discard_comments(input_string), expected_output)

    def test_multiple_hashes_in_string_and_comment(self):
        # Test with multiple hashes, some in string, some as comment
        input_string = (
            'url = "http://example.com/#anchor" # this is a comment about the URL'
        )
        expected_output = 'url = "http://example.com/#anchor"'
        self.assertEqual(discard_comments(input_string), expected_output)

    def test_unclosed_quotes(self):
        # The function's current behavior handles unclosed quotes by continuing
        # to treat everything as if it's inside quotes until the end or another quote.
        # This is an important edge case to document the behavior for.
        input_string = 'text with "unclosed quote # this is treated as string'
        expected_output = 'text with "unclosed quote # this is treated as string'
        self.assertEqual(discard_comments(input_string), expected_output)

        input_string = "text with 'unclosed quote # this is treated as string"
        expected_output = "text with 'unclosed quote # this is treated as string"
        self.assertEqual(discard_comments(input_string), expected_output)

    def test_quote_inside_other_quote_no_comment(self):
        # Example: "text with 'single quotes' inside double"
        input_string = "This is a \"string with 'nested' quotes\" here."
        expected_output = "This is a \"string with 'nested' quotes\" here."
        self.assertEqual(discard_comments(input_string), expected_output)

    def test_quote_inside_other_quote_with_hash(self):
        # Example: "text with 'single quotes #with hash' inside double"
        input_string = "This is a \"string with 'nested #hash' quotes\" here."
        expected_output = "This is a \"string with 'nested #hash' quotes\" here."
        self.assertEqual(discard_comments(input_string), expected_output)

    def test_comment_after_mixed_quotes(self):
        input_string = "'single quote' then \"double quote\" # comment here"
        expected_output = "'single quote' then \"double quote\""
        self.assertEqual(discard_comments(input_string), expected_output)


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)


if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    unittest.main()
