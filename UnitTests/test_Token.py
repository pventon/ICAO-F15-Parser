import unittest

from Tokenizer.Token import Token


class TokenTest(unittest.TestCase):

    def test_token_constructor(self):
        token = Token("Test Token", 11, 22)
        self.assertEqual("Test Token", token.get_token_string())
        self.assertEqual(11, token.get_token_start_index())
        self.assertEqual(22, token.get_token_end_index())

    def test_token_methods(self):
        token = Token("", 0, 0)
        token.set_token_string("Second Token")
        token.set_token_start_index(33)
        token.set_token_end_index(44)
        token.set_token_base_type(111)
        token.set_token_sub_type(222)
        self.assertEqual("Second Token", token.get_token_string())
        self.assertEqual(33, token.get_token_start_index())
        self.assertEqual(44, token.get_token_end_index())
        self.assertEqual(111, token.get_token_base_type())
        self.assertEqual(222, token.get_token_sub_type())


if __name__ == '__main__':
    unittest.main()
