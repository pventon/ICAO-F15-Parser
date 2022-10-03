# This class tokenizes a string looking for tokens separated by caller specified
# whitespace characters, storing each token along with its location where it was
# found in the input string (a tokens start and end index in the source string). The
# individual tokens along with their associated attributes are stored in a 'Tokens'
# class instance.
from Tokenizer.Tokens import Tokens


class Tokenize:

    # The input string containing the tokens to be extracted
    string_to_tokenize = ""

    # Whitespace token delimiter characters
    whitespace = ""

    # List of extracted tokens
    tokens = Tokens()

    # Constructor without a string to tokenize and a default whitespace string ( \n\t\r).
    def __init__(self):
        self.string_to_tokenize = ""
        self.tokens = Tokens()
        self.whitespace = " \n\t\r"

    # Tokenize the string using the assigned whitespace character set. Any character
    # contained in the parameter 'whitespace' will be discarded and treated as whitespace
    # token separators. A string given as "E1 E2 E3" will yield 3 tokens using the default
    # whitespace character set.
    def tokenize(self):
        # type: () -> None
        self.tokens = Tokens()
        idx = 0
        token_text = ""
        for item in self.string_to_tokenize:
            if item in self.whitespace:
                if len(token_text) > 0:
                    self.__save_token(token_text, idx)
                if item in "/":
                    # We have to save the forward slash token
                    self.__save_token(item, idx+1)
                token_text = ""
            else:
                token_text = token_text + item
            idx = idx + 1

        self.__save_token(token_text, idx)

    # Set a string to tokenize
    def set_string_to_tokenize(self, string_to_tokenize=""):
        # type: (str) -> None
        self.string_to_tokenize = string_to_tokenize

    # Retrieve the string that has been tokenized
    def get_string_to_tokenize(self):
        # type: () -> str
        return self.string_to_tokenize

    # Set a string representing the token whitespace delimiter characters
    def set_whitespace(self, whitespace=""):
        # type: (str) -> None
        self.whitespace = whitespace

    # Retrieve the string representing the token whitespace delimiter characters
    def get_whitespace(self):
        # type: () -> str
        return self.whitespace

    # Retrieve the list of tokens
    def get_tokens(self):
        # type: () -> Tokens
        return self.tokens

    # Save a token to a local token attribute
    def __save_token(self, token_text, idx):
        # type: (str, int) -> None
        if len(token_text) > 0:
            self.tokens.create_append_token(
                token_text, idx - len(token_text), idx)
