import unittest

from Tokenizer.Token import Token
from Tokenizer.Tokens import Tokens


class TokensTest(unittest.TestCase):
    tokens = None

    @classmethod
    def setUpClass(cls):
        cls.tokens = Tokens()
        cls.tokens.append_token(Token("Token 1", 1, 1))
        cls.tokens.append_token(Token("Token 2", 2, 2))
        cls.tokens.append_token(Token("Token 3", 3, 3))
        cls.tokens.append_token(Token("Token 4", 4, 4))
        cls.tokens.append_token(Token("Token 5", 5, 5))
        cls.tokens.append_token(Token("Token 6", 6, 6))
        cls.tokens.append_token(Token("Token 7", 7, 7))
        cls.tokens.append_token(Token("Token 8", 8, 8))
        cls.tokens.append_token(Token("Token 9", 9, 9))
        cls.tokens.create_append_token("Token 10", 10, 10)

    def test_tokens_methods_01(self):
        self.assertEqual("Token 1", self.tokens.get_first_token().get_token_string())
        self.assertEqual("Token 2", self.tokens.get_next_token().get_token_string())
        self.assertEqual("Token 3", self.tokens.get_next_token().get_token_string())
        self.assertEqual("Token 4", self.tokens.get_next_token().get_token_string())
        self.assertEqual("Token 5", self.tokens.get_next_token().get_token_string())
        self.assertEqual("Token 6", self.tokens.get_next_token().get_token_string())
        self.assertEqual("Token 7", self.tokens.get_next_token().get_token_string())
        self.assertEqual("Token 8", self.tokens.get_next_token().get_token_string())
        self.assertEqual("Token 9", self.tokens.get_next_token().get_token_string())
        self.assertEqual("Token 10", self.tokens.get_next_token().get_token_string())

    def test_tokens_methods_02(self):
        self.assertEqual(10, self.tokens.get_number_of_tokens())
        token_list = self.tokens.get_tokens()
        self.assertEqual("Token 7", token_list[6].get_token_string())

    def test_tokens_methods_03(self):
        self.assertEqual("Token 1", self.tokens.get_first_token().get_token_string())
        self.assertEqual("Token 2", self.tokens.get_next_token().get_token_string())
        self.assertEqual("Token 10", self.tokens.get_last_token().get_token_string())
        self.assertEqual("Token 9", self.tokens.get_previous_token().get_token_string())
        self.assertEqual("Token 8", self.tokens.get_previous_token().get_token_string())
        self.assertEqual("Token 7", self.tokens.get_previous_token().get_token_string())
        self.assertEqual("Token 6", self.tokens.get_previous_token().get_token_string())
        self.assertEqual("Token 6", self.tokens.get_current_token().get_token_string())
        self.assertEqual("Token 5", self.tokens.get_previous_token().get_token_string())
        self.assertEqual("Token 7", self.tokens.peek_next_token(2).get_token_string())
        self.assertEqual("Token 2", self.tokens.peek_previous_token(3).get_token_string())


if __name__ == '__main__':
    unittest.main()
