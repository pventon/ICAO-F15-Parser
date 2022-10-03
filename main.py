from Parser.ExtractedRouteSequence import ExtractedRouteSequence
from Parser.F15Parse import ParseF15
from Tokenizer.Tokenize import Tokenize

# Example usage of the ICAO field 15 parser.
# A sample Field 15 string...
#                         1         2         3         4         5         6         7         8
#               012345678901234567890123456789012345678901234567890123456789012345678901234567890
token_string = "N0450M0825 00N000E B9 00N001E VFR IFR 00N001W/N0350F100 01N001W 01S001W 02S001W180060"

# Instantiate the tokenizer; the 'Tokenize()' class is stateless and thread safe
# and can be used 'n' times for multi threading parallel processing purposes.
tokenize = Tokenize()

# Set the string to be tokenized
tokenize.set_string_to_tokenize(token_string)

# Set the white space to tokenize the ICAO field 15, these are a space (ASCII 20),
# a newline (\n), a tab (\t), a carriage return (\r) and the forward slash (/).
# The forward slash is always saved as a token, the remaining whitespace characters
# are discarded.
tokenize.set_whitespace(" \n\t\r/")

# Tokenize the Field 15 string
tokenize.tokenize()

# The tokenized list of tokens is stored in a list which can be retrieved.
tokens = tokenize.get_tokens()

# Instantiate an Extracted Route Record instance
ers = ExtractedRouteSequence()

# Past the input tokens and output storage as parameters to the parser.
# If the error count returned is greater than zero then errors exist.
# It is a callers responsibility to retrieve the erroneous tokens with
# ers.get_all_errors() which returns a list of tokens containing all
# error cases. The erroneous tokens have their start and end index
# describing their location in field 15 which means these can be
# used to highlight erroneous token in a GUI.
num_errors = ParseF15().parse_f15(ers, tokens)

# An ERS can be examined with the following print command...
ers.print_ers()

