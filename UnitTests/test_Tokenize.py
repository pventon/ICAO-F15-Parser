import unittest

from Tokenizer.Tokenize import Tokenize


class TokenizeTest(unittest.TestCase):

    def test_tokenize_constructor_01(self):
        tokenizer = Tokenize()
        self.assertEqual(0, tokenizer.get_tokens().get_number_of_tokens())

    def test_tokenize_constructor_02(self):
        tokenizer = Tokenize()
        tokenizer.set_string_to_tokenize("Token1 Token2\nToken3\rToken4\tToken5 \n \t \r Token6  \r\r\r    Token7")
        tokenizer.tokenize()
        self.assertEqual(7, tokenizer.get_tokens().get_number_of_tokens())
        self.assertEqual("Token1", tokenizer.get_tokens().get_first_token().get_token_string())
        self.assertEqual("Token2", tokenizer.get_tokens().get_next_token().get_token_string())
        self.assertEqual("Token3", tokenizer.get_tokens().get_next_token().get_token_string())
        self.assertEqual("Token4", tokenizer.get_tokens().get_next_token().get_token_string())
        self.assertEqual("Token5", tokenizer.get_tokens().get_next_token().get_token_string())
        self.assertEqual("Token6", tokenizer.get_tokens().get_next_token().get_token_string())
        self.assertEqual("Token7", tokenizer.get_tokens().get_next_token().get_token_string())

    def test_tokenize_constructor_03(self):
        tokenizer = Tokenize()
        tokenizer.set_string_to_tokenize("T1 T2\nT3\rT4\tT5 \n \t \r T6  \r\r\r    T7-T8 - T9")
        tokenizer.set_whitespace(" \n\t\r-")
        tokenizer.tokenize()
        self.assertEqual(9, tokenizer.get_tokens().get_number_of_tokens())
        self.assertEqual("T1", tokenizer.get_tokens().get_first_token().get_token_string())
        self.assertEqual("T2", tokenizer.get_tokens().get_next_token().get_token_string())
        self.assertEqual("T3", tokenizer.get_tokens().get_next_token().get_token_string())
        self.assertEqual("T4", tokenizer.get_tokens().get_next_token().get_token_string())
        self.assertEqual("T5", tokenizer.get_tokens().get_next_token().get_token_string())
        self.assertEqual("T6", tokenizer.get_tokens().get_next_token().get_token_string())
        self.assertEqual("T7", tokenizer.get_tokens().get_next_token().get_token_string())
        self.assertEqual("T8", tokenizer.get_tokens().get_next_token().get_token_string())
        self.assertEqual("T9", tokenizer.get_tokens().get_next_token().get_token_string())

    def test_tokenize_constructor_04(self):
        tokenizer = Tokenize()
        tokenizer.set_string_to_tokenize("T1 T2\nT3\rT4\tT5 \n \t \r T6  \r\r\r    T7-T8 - T9")
        tokenizer.tokenize()
        tokenizer.set_string_to_tokenize("R1 R2 R3 R4 R5 R6 R7 R8")
        tokenizer.tokenize()
        self.assertEqual(8, tokenizer.get_tokens().get_number_of_tokens())
        self.assertEqual("R1", tokenizer.get_tokens().get_first_token().get_token_string())
        self.assertEqual("R2", tokenizer.get_tokens().get_next_token().get_token_string())
        self.assertEqual("R3", tokenizer.get_tokens().get_next_token().get_token_string())
        self.assertEqual("R4", tokenizer.get_tokens().get_next_token().get_token_string())
        self.assertEqual("R5", tokenizer.get_tokens().get_next_token().get_token_string())
        self.assertEqual("R6", tokenizer.get_tokens().get_next_token().get_token_string())
        self.assertEqual("R7", tokenizer.get_tokens().get_next_token().get_token_string())
        self.assertEqual("R8", tokenizer.get_tokens().get_next_token().get_token_string())


if __name__ == '__main__':
    unittest.main()
