import unittest

from Parser.ExtractedRouteSequence import ExtractedRouteSequence
from Parser.F15Parse import ParseF15
from Tokenizer.Tokenize import Tokenize


class XmlOutputTest(unittest.TestCase):
    tokens = None
    tokenizer = None
    ers = None

    @classmethod
    def setUpClass(cls):
        cls.tokenizer = Tokenize()
        cls.tokenizer.set_whitespace(" \n\t\r/")
        cls.ers = ExtractedRouteSequence()

    def test_as_xml_01(self):
        # Test a simple non-error case
        self.__parse_field_15("N0450F350 PNT")
        # print(self.ers.as_xml())

    def test_as_xml_02(self):
        # Test a error case
        self.__parse_field_15("N0450F350 PNT DEF% GGG")
        # print(self.ers.as_xml())

    def test_as_xml_03(self):
        # Test with break text
        self.__parse_field_15("N0450F350 PNT/N0100VFR THIS IS VFR TEXT")
        # print(self.ers.as_xml())

    def test_as_xml_04(self):
        # Test lat/long
        self.__parse_field_15("N0450F350 12N123W 13N023W")
        # print(self.ers.as_xml())

    def __get_error_text_at(self, idx):
        # print(self.ers.get_all_errors()[idx].get_error_text())
        return self.ers.get_all_errors()[idx].get_error_text()

    def __parse_field_15(self, field_15):
        self.tokenizer.set_string_to_tokenize(field_15)
        self.tokenizer.tokenize()
        self.ers = ExtractedRouteSequence()
        return ParseF15().parse_f15(self.ers, self.tokenizer.get_tokens())


if __name__ == '__main__':
    unittest.main()
