import unittest

from Parser.ExtractedRouteSequence import ExtractedRouteSequence
from Parser.F15Parse import ParseF15
from Tokenizer.Tokenize import Tokenize


class F15ParserTest(unittest.TestCase):
    tokens = None
    tokenizer = None
    ers = None

    @classmethod
    def setUpClass(cls):
        cls.tokenizer = Tokenize()
        cls.tokenizer.set_whitespace(" \n\t\r/")
        cls.ers = ExtractedRouteSequence()

    def test_parse_f15(self):
        # Empty field 15
        self.__parse_field_15("")
        self.assertEqual("ADEP", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Field 15 is empty", self.__get_error_text_at(0))

        # Field 15 does not start with a speed / level or speed / VFR token.
        self.__parse_field_15("B9")
        self.assertEqual("ADEP", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The first Field 15 element must be a SPEED/LEVEL and not 'B9'", self.__get_error_text_at(0))

        # No route description provided for pure IFR start
        self.__parse_field_15("N0450F350")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Field 15 contains no route description", self.__get_error_text_at(0))

        # Nothing following initial speed / VFR element
        self.__parse_field_15("N0450VFR")
        self.assertEqual("ADEP VFR N0450 F050", self.ers.get_first_element().unit_test_only())
        self.assertEqual("VFR VFR N0450 F050", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # VFR text following initial speed / VFR element
        self.__parse_field_15("N0450VFR THIS IS VFR TEXT")
        self.assertEqual("ADEP VFR N0450 F050", self.ers.get_first_element().unit_test_only())
        self.assertEqual("VFR VFR N0450 F050 THIS IS VFR TEXT", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

    def test_post_adep(self):
        # Unknown item following first speed / level
        self.__parse_field_15("N0450F350 6B6B")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The element '6B6B' is an unrecognised Field 15 element", self.__get_error_text_at(0))

        # '/' following first speed / level
        self.__parse_field_15("N0450F350 /")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The first SPEED/LEVEL cannot be followed by the element '/'", self.__get_error_text_at(0))

        # Break start (VFR, OAT or IFPSTART) following first speed / level
        self.__parse_field_15("N0450F350 VFR")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The first SPEED/LEVEL cannot be followed by the element 'VFR'",
                         self.__get_error_text_at(0))

        # Break end (IFR, GAT or IFPSTOP) following first speed / level
        self.__parse_field_15("N0450F350 IFPSTOP")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The first SPEED/LEVEL cannot be followed by the element 'IFPSTOP'",
                         self.__get_error_text_at(0))

        # Speed / VFR following first speed / level
        self.__parse_field_15("N0450F350 N0100VFR")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The first SPEED/LEVEL cannot be followed by the element 'N0100VFR'",
                         self.__get_error_text_at(0))

        # Speed / level following first speed / level
        self.__parse_field_15("N0450F350 N0100F100")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The first SPEED/LEVEL cannot be followed by the element 'N0100F100'",
                         self.__get_error_text_at(0))

        # STAYn following first speed / level
        self.__parse_field_15("N0450F350 STAY1")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The first SPEED/LEVEL cannot be followed by the element 'STAY1'",
                         self.__get_error_text_at(0))

        # Start of cruise climb following first speed / level
        self.__parse_field_15("N0450F350 C")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The first SPEED/LEVEL cannot be followed by the element 'C'",
                         self.__get_error_text_at(0))

        # DCT following first speed / level
        self.__parse_field_15("N0450F350 DCT")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("DCT IFR N0450 F350", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Truncate following first speed / level
        self.__parse_field_15("N0450F350 T")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Point following first speed / level
        self.__parse_field_15("N0450F350 PNT")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("PNT IFR N0450 F350", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Route following first speed / level
        self.__parse_field_15("N0450F350 B9")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting SID or DPF after first SPEED/LEVEL element instead of 'B9'",
                         self.__get_error_text_at(0))

        # SID / STAR following first speed / level
        self.__parse_field_15("N0450F350 LNZ1A")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("LNZ1A IFR N0450 F350", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Speed / level / level following first speed / level
        self.__parse_field_15("N0450F350 N0100F100F200")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting 'C/POINT/' before 'N0100F100F200'", self.__get_error_text_at(0))

        # Speed / level / PLUS following first speed / level
        self.__parse_field_15("N0450F350 N0100F100PLUS")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting 'C/POINT/' before 'N0100F100PLUS'", self.__get_error_text_at(0))

        # Token too long following first speed / level
        self.__parse_field_15("N0450F350 ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Element 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' is too long for a Field 15 Element",
                         self.__get_error_text_at(0))

        # Stay time following first speed / level
        self.__parse_field_15("N0450F350 1234")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting the keyword 'STAY' before '1234'", self.__get_error_text_at(0))

        # SID following first speed / level
        self.__parse_field_15("N0450F350 SID")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("SID IFR N0450 F350", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # STAR following first speed / level
        self.__parse_field_15("N0450F350 STAR")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("STAR IFR N0450 F350", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

    def test_post_point(self):
        # Unknown item following point
        self.__parse_field_15("N0450F250 PNT 6B6B")
        self.assertEqual("ADEP IFR N0450 F250", self.ers.get_first_element().unit_test_only())
        self.assertEqual("PNT IFR N0450 F250", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The element '6B6B' is an unrecognised Field 15 element", self.__get_error_text_at(0))

        # '/' item following point
        self.__parse_field_15("M082F350 PNT /")
        self.assertEqual("ADEP IFR M082 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("PNT IFR M082 F350", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Field 15 is incomplete, expecting additional data after the final '/'",
                         self.__get_error_text_at(0))

        # Break start item following point
        self.__parse_field_15("N0450F350 PNT OAT OAT/G A T BREAK TEXT")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("PNT IFR N0450 F350", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("OAT OAT N0450 F350 OAT / G A T BREAK TEXT", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES OAT", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Speed / VFR item following point
        self.__parse_field_15("N0150F350 PNT N0100VFR")
        self.assertEqual("ADEP IFR N0150 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("PNT IFR N0150 F350", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting '/' before 'N0100VFR'", self.__get_error_text_at(0))

        # Break end item following point
        self.__parse_field_15("N0440F350 PNT GAT")
        self.assertEqual("ADEP IFR N0440 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("PNT IFR N0440 F350", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("No OAT section preceding this 'GAT' rule change indicator", self.__get_error_text_at(0))

        # DCT item following point
        self.__parse_field_15("N0450F350 PNT DCT")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("PNT IFR N0450 F350", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("DCT IFR N0450 F350", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # STAYn item following point
        self.__parse_field_15("N0410F350 PNT STAY1")
        self.assertEqual("ADEP IFR N0410 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("PNT IFR N0410 F350", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting STAY time as '/HHMM' after 'STAY1'", self.__get_error_text_at(0))

        # Truncate item following point
        self.__parse_field_15("N0390F350 PNT T")
        self.assertEqual("ADEP IFR N0390 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("PNT IFR N0390 F350", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # 'C' (from cruise climb) item following point
        self.__parse_field_15("K0450F350 PNT C")
        self.assertEqual("ADEP IFR K0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("PNT IFR K0450 F350", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("C IFR K0450 F350", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Point item following point
        self.__parse_field_15("N0450F350 PNT SBG")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("PNT IFR N0450 F350", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("SBG IFR N0450 F350", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Route item following point
        self.__parse_field_15("N0450F350 PNT A8")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("PNT IFR N0450 F350", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("A8 IFR N0450 F350", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # SID or STAR item following point
        self.__parse_field_15("N0450F350 PNT LNZ1A")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("PNT IFR N0450 F350", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("LNZ1A IFR N0450 F350", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Speed / level item following point
        self.__parse_field_15("N0450A350 PNT N0300F100")
        self.assertEqual("ADEP IFR N0450 A350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("PNT IFR N0450 A350", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting '/' before 'N0300F100'", self.__get_error_text_at(0))

        # Speed / level / level item following point
        self.__parse_field_15("N0450S0350 PNT N0200F100F200")
        self.assertEqual("ADEP IFR N0450 S0350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("PNT IFR N0450 S0350", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting 'C/POINT/' before 'N0200F100F200'", self.__get_error_text_at(0))

        # Speed / Level / PLUS item following point
        self.__parse_field_15("N0450S0150 PNT N0150F150PLUS")
        self.assertEqual("ADEP IFR N0450 S0150", self.ers.get_first_element().unit_test_only())
        self.assertEqual("PNT IFR N0450 S0150", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting 'C/POINT/' before 'N0150F150PLUS'", self.__get_error_text_at(0))

        # Too long item following point
        self.__parse_field_15("K0990A300 PNT ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.assertEqual("ADEP IFR K0990 A300", self.ers.get_first_element().unit_test_only())
        self.assertEqual("PNT IFR K0990 A300", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Element 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' is too long for a Field 15 Element",
                         self.__get_error_text_at(0))

        # Stay time item following point
        self.__parse_field_15("N0450M0800 PNT 2256")
        self.assertEqual("ADEP IFR N0450 M0800", self.ers.get_first_element().unit_test_only())
        self.assertEqual("PNT IFR N0450 M0800", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting the keyword 'STAY' before '2256'", self.__get_error_text_at(0))

        # SID item following point
        self.__parse_field_15("N0450A700 PNT LNZ1A")
        self.assertEqual("ADEP IFR N0450 A700", self.ers.get_first_element().unit_test_only())
        self.assertEqual("PNT IFR N0450 A700", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("LNZ1A IFR N0450 A700", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # STAR item following point
        self.__parse_field_15("N0450F350 PNT NOLAN2C")
        self.assertEqual("ADEP IFR N0450 F350", self.ers.get_first_element().unit_test_only())
        self.assertEqual("PNT IFR N0450 F350", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("NOLAN2C IFR N0450 F350", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

    def test_re_sync_parser_after_error(self):
        # Unknown item following erroneous item
        self.__parse_field_15("N0450M0825 N0100VFR B8B8")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(2, self.ers.get_number_of_errors())
        self.assertEqual("The first SPEED/LEVEL cannot be followed by the element 'N0100VFR'",
                         self.__get_error_text_at(0))
        self.assertEqual("The element 'B8B8' is an unrecognised Field 15 element",
                         self.__get_error_text_at(1))

        # '/' item following erroneous item
        self.__parse_field_15("N0450M0700 B9 /")
        self.assertEqual("ADEP IFR N0450 M0700", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(2, self.ers.get_number_of_errors())
        self.assertEqual("Expecting SID or DPF after first SPEED/LEVEL element instead of 'B9'",
                         self.__get_error_text_at(0))
        self.assertEqual("Field 15 cannot end with the '/' element",
                         self.__get_error_text_at(1))

        # '/' speed / VFR items following erroneous item
        self.__parse_field_15("N0450M0800 B9 /N0100VFR")
        self.assertEqual("ADEP IFR N0100 F050", self.ers.get_first_element().unit_test_only())
        self.assertEqual("VFR VFR N0100 F050", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting SID or DPF after first SPEED/LEVEL element instead of 'B9'",
                         self.__get_error_text_at(0))

        # '/' Point items following erroneous item
        self.__parse_field_15("N0450M0800 B9 / ABCDE")
        self.assertEqual("ADEP IFR N0450 M0800", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABCDE IFR N0450 M0800", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting SID or DPF after first SPEED/LEVEL element instead of 'B9'",
                         self.__get_error_text_at(0))

        # '/' Speed / level items following erroneous item
        self.__parse_field_15("N0450M0800 B9 /N0100F200")
        self.assertEqual("ADEP IFR N0100 F200", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting SID or DPF after first SPEED/LEVEL element instead of 'B9'",
                         self.__get_error_text_at(0))

        # '/' Speed / level / level items following erroneous item
        self.__parse_field_15("N0450M0800 B9 /N0100F210F300")
        self.assertEqual("ADEP IFR N0100 F210", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting SID or DPF after first SPEED/LEVEL element instead of 'B9'",
                         self.__get_error_text_at(0))

        # '/' Speed / level / Plus items following erroneous item
        self.__parse_field_15("N0450M0800 B9 /N0230F130PLUS")
        self.assertEqual("ADEP IFR N0230 F130", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting SID or DPF after first SPEED/LEVEL element instead of 'B9'",
                         self.__get_error_text_at(0))

        # '/' Route items following erroneous item
        self.__parse_field_15("N0450M0800 B9 / B9")
        self.assertEqual("ADEP IFR N0450 M0800", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(2, self.ers.get_number_of_errors())
        self.assertEqual("Expecting SID or DPF after first SPEED/LEVEL element instead of 'B9'",
                         self.__get_error_text_at(0))
        self.assertEqual("'/' not expected preceding 'B9'",
                         self.__get_error_text_at(1))

        # Break start item following erroneous item
        self.__parse_field_15("N0450M0800 N0100VFR IFPSTOP")
        self.assertEqual("ADEP IFR N0450 M0800", self.ers.get_first_element().unit_test_only())
        self.assertEqual("IFPSTOP IFPS N0450 M0800", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFPS", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The first SPEED/LEVEL cannot be followed by the element 'N0100VFR'",
                         self.__get_error_text_at(0))

        # Speed / VFR item following erroneous item
        self.__parse_field_15("N0450M0800 STAY6 N0110VFR")
        self.assertEqual("ADEP IFR N0110 F050", self.ers.get_first_element().unit_test_only())
        self.assertEqual("VFR VFR N0110 F050", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The first SPEED/LEVEL cannot be followed by the element 'STAY6'",
                         self.__get_error_text_at(0))

        # Break end item following erroneous item
        self.__parse_field_15("N0450M0800 N0100VFR IFR")
        self.assertEqual("ADEP IFR N0450 M0800", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The first SPEED/LEVEL cannot be followed by the element 'N0100VFR'",
                         self.__get_error_text_at(0))

        # DCT item following erroneous item
        self.__parse_field_15("N0450M0800 N0100VFR DCT")
        self.assertEqual("ADEP IFR N0450 M0800", self.ers.get_first_element().unit_test_only())
        self.assertEqual("DCT IFR N0450 M0800", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The first SPEED/LEVEL cannot be followed by the element 'N0100VFR'",
                         self.__get_error_text_at(0))

        # STAYn item following erroneous item
        self.__parse_field_15("N0450M0650 N0100VFR STAY2")
        self.assertEqual("ADEP IFR N0450 M0650", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(2, self.ers.get_number_of_errors())
        self.assertEqual("The first SPEED/LEVEL cannot be followed by the element 'N0100VFR'",
                         self.__get_error_text_at(0))
        self.assertEqual("Expecting STAY time as '/HHMM' after 'STAY2'",
                         self.__get_error_text_at(1))

        # Truncate item following erroneous item
        self.__parse_field_15("N0450M0500 N0100VFR T")
        self.assertEqual("ADEP IFR N0450 M0500", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The first SPEED/LEVEL cannot be followed by the element 'N0100VFR'",
                         self.__get_error_text_at(0))

        # 'C' (start of cruise climb) item following erroneous item
        self.__parse_field_15("N0450M0800 N0100VFR C")
        self.assertEqual("ADEP IFR N0450 M0800", self.ers.get_first_element().unit_test_only())
        self.assertEqual("C IFR N0450 M0800", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The first SPEED/LEVEL cannot be followed by the element 'N0100VFR'",
                         self.__get_error_text_at(0))

        # Point item following erroneous item
        self.__parse_field_15("N0450M0800 N0100VFR GHGIK")
        self.assertEqual("ADEP IFR N0450 M0800", self.ers.get_first_element().unit_test_only())
        self.assertEqual("GHGIK IFR N0450 M0800", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The first SPEED/LEVEL cannot be followed by the element 'N0100VFR'",
                         self.__get_error_text_at(0))

        # Route item following erroneous item
        self.__parse_field_15("N0450M0800 N0100VFR B8")
        self.assertEqual("ADEP IFR N0450 M0800", self.ers.get_first_element().unit_test_only())
        self.assertEqual("B8 IFR N0450 M0800", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The first SPEED/LEVEL cannot be followed by the element 'N0100VFR'",
                         self.__get_error_text_at(0))

        # SID / STAR item following erroneous item
        self.__parse_field_15("N0450M0800 N0100VFR SBG5R")
        self.assertEqual("ADEP IFR N0450 M0800", self.ers.get_first_element().unit_test_only())
        self.assertEqual("SBG5R IFR N0450 M0800", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The first SPEED/LEVEL cannot be followed by the element 'N0100VFR'",
                         self.__get_error_text_at(0))

        # Speed / level item following erroneous item
        self.__parse_field_15("N0450M0800 N0100VFR N0200F120")
        self.assertEqual("ADEP IFR N0200 F120", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The first SPEED/LEVEL cannot be followed by the element 'N0100VFR'",
                         self.__get_error_text_at(0))

        # Speed / level / level item following erroneous item
        self.__parse_field_15("N0450M0800 N0100VFR K0234S3423A123")
        self.assertEqual("ADEP IFR K0234 S3423", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The first SPEED/LEVEL cannot be followed by the element 'N0100VFR'",
                         self.__get_error_text_at(0))

        # Speed /level / PLUS item following erroneous item
        self.__parse_field_15("N0450M0800 N0100VFR M070F100M1000")
        self.assertEqual("ADEP IFR M070 F100", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The first SPEED/LEVEL cannot be followed by the element 'N0100VFR'",
                         self.__get_error_text_at(0))

        # Too long item following erroneous item
        self.__parse_field_15("N0450M0800 N0100VFR ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.assertEqual("ADEP IFR N0450 M0800", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(2, self.ers.get_number_of_errors())
        self.assertEqual("The first SPEED/LEVEL cannot be followed by the element 'N0100VFR'",
                         self.__get_error_text_at(0))
        self.assertEqual("Element 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' is too long for a Field 15 Element",
                         self.__get_error_text_at(1))

        # Stay time item following erroneous item
        self.__parse_field_15("N0450M0400 N0100VFR 2359")
        self.assertEqual("ADEP IFR N0450 M0400", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual(2, self.ers.get_number_of_errors())
        self.assertEqual("The first SPEED/LEVEL cannot be followed by the element 'N0100VFR'",
                         self.__get_error_text_at(0))
        self.assertEqual("Expecting the keyword 'STAY' before '2359'",
                         self.__get_error_text_at(1))

        # SID item following erroneous item
        self.__parse_field_15("N0450M0800 N0100VFR JKL0R")
        self.assertEqual("ADEP IFR N0450 M0800", self.ers.get_first_element().unit_test_only())
        self.assertEqual("JKL0R IFR N0450 M0800", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The first SPEED/LEVEL cannot be followed by the element 'N0100VFR'",
                         self.__get_error_text_at(0))

        # STAR item following erroneous item
        self.__parse_field_15("N0450M0800 N0100VFR NOLAN8Y")
        self.assertEqual("ADEP IFR N0450 M0800", self.ers.get_first_element().unit_test_only())
        self.assertEqual("NOLAN8Y IFR N0450 M0800", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The first SPEED/LEVEL cannot be followed by the element 'N0100VFR'",
                         self.__get_error_text_at(0))

    def test_break_end(self):
        # No point following rule change back to IFR
        self.__parse_field_15("N0450M0825 BGH VFR THIS IS VFR TEXT IFR")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0825 THIS IS VFR TEXT IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # No point following rule change back to GAT
        self.__parse_field_15("N0450M0825 BGH OAT THIS IS OAT TEXT GAT")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("OAT OAT N0450 M0825 THIS IS OAT TEXT GAT", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES OAT", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # No point following rule change back to IFPSTART
        self.__parse_field_15("N0450M0825 BGH IFPSTOP THIS IS OAT TEXT IFPSTART")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("IFPSTOP IFPS N0450 M0825 THIS IS OAT TEXT IFPSTART",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFPS", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Unknown item following rule change back to IFR
        self.__parse_field_15("N0450M0825 BGH VFR THIS IS VFR TEXT IFR B8B8")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0825 THIS IS VFR TEXT IFR B8B8",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Unknown item following rule change back to GAT
        self.__parse_field_15("N0450M0825 BGH OAT THIS IS OAT TEXT GAT B8B8")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("OAT OAT N0450 M0825 THIS IS OAT TEXT GAT B8B8",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES OAT", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Unknown item following rule change back to IFPSTART
        self.__parse_field_15("N0450M0825 BGH IFPSTOP THIS IS OAT TEXT IFPSTART B8B8")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("IFPSTOP IFPS N0450 M0825 THIS IS OAT TEXT IFPSTART B8B8",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFPS", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # '/' item following rule change back to IFR
        self.__parse_field_15("N0450M0825 BGH VFR THIS IS VFR TEXT IFR / ")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0825 THIS IS VFR TEXT IFR /", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # '/' item following rule change back to GAT
        self.__parse_field_15("N0450M0825 BGH OAT THIS IS OAT TEXT GAT /")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("OAT OAT N0450 M0825 THIS IS OAT TEXT GAT /", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES OAT", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # '/' item following rule change back to IFPSTART
        self.__parse_field_15("N0450M0825 BGH IFPSTOP THIS IS OAT TEXT IFPSTART /")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("IFPSTOP IFPS N0450 M0825 THIS IS OAT TEXT IFPSTART /",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFPS", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Break start item following rule change back to IFR
        self.__parse_field_15("N0450M0825 BGH VFR THIS IS VFR TEXT IFR VFR")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0825 THIS IS VFR TEXT IFR VFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Break start item following rule change back to GAT
        self.__parse_field_15("N0450M0825 BGH OAT THIS IS OAT TEXT GAT OAT")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("OAT OAT N0450 M0825 THIS IS OAT TEXT GAT OAT", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES OAT", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Break start item following rule change back to IFPSTART
        self.__parse_field_15("N0450M0825 BGH IFPSTOP THIS IS OAT TEXT IFPSTART IFPSTOP")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("IFPSTOP IFPS N0450 M0825 THIS IS OAT TEXT IFPSTART IFPSTOP",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFPS", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Speed / VFR item following rule change back to IFR
        self.__parse_field_15("N0450M0825 BGH VFR THIS IS VFR TEXT IFR N0450VFR")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0825 THIS IS VFR TEXT IFR N0450VFR",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Speed / VFR item following rule change back to GAT
        self.__parse_field_15("N0450M0825 BGH OAT THIS IS OAT TEXT GAT N0450VFR")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("OAT OAT N0450 M0825 THIS IS OAT TEXT GAT N0450VFR",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES OAT", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Speed / VFR item following rule change back to IFPSTART
        self.__parse_field_15("N0450M0825 BGH IFPSTOP THIS IS OAT TEXT IFPSTART N0450VFR")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("IFPSTOP IFPS N0450 M0825 THIS IS OAT TEXT IFPSTART N0450VFR",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFPS", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Break end item following rule change back to IFR
        self.__parse_field_15("N0450M0825 BGH VFR THIS IS VFR TEXT IFR IFR")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0825 THIS IS VFR TEXT IFR IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Break end item following rule change back to GAT
        self.__parse_field_15("N0450M0825 BGH OAT THIS IS OAT TEXT GAT GAT")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("OAT OAT N0450 M0825 THIS IS OAT TEXT GAT GAT", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES OAT", self.ers.get_element_at(3).unit_test_only())

        # Break end item following rule change back to IFPSTART
        self.__parse_field_15("N0450M0825 BGH IFPSTOP THIS IS OAT TEXT IFPSTART IFPSTART")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("IFPSTOP IFPS N0450 M0825 THIS IS OAT TEXT IFPSTART IFPSTART",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFPS", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # DCT item following rule change back to IFR
        self.__parse_field_15("N0450M0825 BGH VFR THIS IS VFR TEXT IFR DCT")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0825 THIS IS VFR TEXT IFR DCT", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # DCT item following rule change back to GAT
        self.__parse_field_15("N0450M0825 BGH OAT THIS IS OAT TEXT GAT DCT")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("OAT OAT N0450 M0825 THIS IS OAT TEXT GAT DCT", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES OAT", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # DCT item following rule change back to IFPSTART
        self.__parse_field_15("N0450M0825 BGH IFPSTOP THIS IS OAT TEXT IFPSTART DCT")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("IFPSTOP IFPS N0450 M0825 THIS IS OAT TEXT IFPSTART DCT",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFPS", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # STAY item following rule change back to IFR
        self.__parse_field_15("N0450M0825 BGH VFR THIS IS VFR TEXT IFR STAY3")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0825 THIS IS VFR TEXT IFR STAY3", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # STAY item following rule change back to GAT
        self.__parse_field_15("N0450M0825 BGH OAT THIS IS OAT TEXT GAT STAY3")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("OAT OAT N0450 M0825 THIS IS OAT TEXT GAT STAY3", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES OAT", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # STAY item following rule change back to IFPSTART
        self.__parse_field_15("N0450M0825 BGH IFPSTOP THIS IS OAT TEXT IFPSTART STAY3")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("IFPSTOP IFPS N0450 M0825 THIS IS OAT TEXT IFPSTART STAY3",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFPS", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Truncate item following rule change back to IFR
        self.__parse_field_15("N0450M0825 BGH VFR THIS IS VFR TEXT IFR T")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0825 THIS IS VFR TEXT IFR T", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Truncate item following rule change back to GAT
        self.__parse_field_15("N0450M0825 BGH OAT THIS IS OAT TEXT GAT T")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("OAT OAT N0450 M0825 THIS IS OAT TEXT GAT T", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES OAT", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Truncate item following rule change back to IFPSTART
        self.__parse_field_15("N0450M0825 BGH IFPSTOP THIS IS OAT TEXT IFPSTART T")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("IFPSTOP IFPS N0450 M0825 THIS IS OAT TEXT IFPSTART T",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFPS", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # 'C' item following rule change back to IFR
        self.__parse_field_15("N0450M0825 BGH VFR THIS IS VFR TEXT IFR C")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0825 THIS IS VFR TEXT IFR C", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # 'C' item following rule change back to GAT
        self.__parse_field_15("N0450M0825 BGH OAT THIS IS OAT TEXT GAT C")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("OAT OAT N0450 M0825 THIS IS OAT TEXT GAT C", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES OAT", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # 'C' item following rule change back to IFPSTART
        self.__parse_field_15("N0450M0825 BGH IFPSTOP THIS IS OAT TEXT IFPSTART C")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("IFPSTOP IFPS N0450 M0825 THIS IS OAT TEXT IFPSTART C",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFPS", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Point item following rule change back to IFR
        self.__parse_field_15("N0450M0825 BGH VFR THIS IS VFR TEXT IFR ABC")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0825 THIS IS VFR TEXT IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ABC IFR N0450 M0825", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(4).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting '/SPEED/LEVEL' following 'ABC' to complete rule change to IFR",
                         self.__get_error_text_at(0))

        # Point item following rule change back to GAT
        self.__parse_field_15("N0450M0825 BGH OAT THIS IS OAT TEXT GAT ABC")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("OAT OAT N0450 M0825 THIS IS OAT TEXT GAT", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ABC IFR N0450 M0825", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(4).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Point item following rule change back to IFPSTART
        self.__parse_field_15("N0450M0825 BGH IFPSTOP THIS IS OAT TEXT IFPSTART ABC")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("IFPSTOP IFPS N0450 M0825 THIS IS OAT TEXT IFPSTART",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ABC IFR N0450 M0825", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(4).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Route item following rule change back to IFR
        self.__parse_field_15("N0450M0825 BGH VFR THIS IS VFR TEXT IFR A3")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0825 THIS IS VFR TEXT IFR A3", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Route item following rule change back to GAT
        self.__parse_field_15("N0450M0825 BGH OAT THIS IS OAT TEXT GAT A3")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("OAT OAT N0450 M0825 THIS IS OAT TEXT GAT A3", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES OAT", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Route item following rule change back to IFPSTART
        self.__parse_field_15("N0450M0825 BGH IFPSTOP THIS IS OAT TEXT IFPSTART A3")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("IFPSTOP IFPS N0450 M0825 THIS IS OAT TEXT IFPSTART A3",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFPS", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # SID / STAR item following rule change back to IFR
        self.__parse_field_15("N0450M0825 BGH VFR THIS IS VFR TEXT IFR LNZ1G")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0825 THIS IS VFR TEXT IFR LNZ1G", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # SID / STAR item following rule change back to GAT
        self.__parse_field_15("N0450M0825 BGH OAT THIS IS OAT TEXT GAT LNZ1G")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("OAT OAT N0450 M0825 THIS IS OAT TEXT GAT LNZ1G", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES OAT", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # SID / STAR item following rule change back to IFPSTART
        self.__parse_field_15("N0450M0825 BGH IFPSTOP THIS IS OAT TEXT IFPSTART LNZ1G")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("IFPSTOP IFPS N0450 M0825 THIS IS OAT TEXT IFPSTART LNZ1G",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFPS", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Speed / level item following rule change back to IFR
        self.__parse_field_15("N0450M0825 BGH VFR THIS IS VFR TEXT IFR N0100F200")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0825 THIS IS VFR TEXT IFR N0100F200",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Speed / level item following rule change back to GAT
        self.__parse_field_15("N0450M0825 BGH OAT THIS IS OAT TEXT GAT N0100F200")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("OAT OAT N0450 M0825 THIS IS OAT TEXT GAT N0100F200",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES OAT", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Speed / level item following rule change back to IFPSTART
        self.__parse_field_15("N0450M0825 BGH IFPSTOP THIS IS OAT TEXT IFPSTART N0100F200")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("IFPSTOP IFPS N0450 M0825 THIS IS OAT TEXT IFPSTART N0100F200",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFPS", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Speed / level / level item following rule change back to IFR
        self.__parse_field_15("N0450M0825 BGH VFR THIS IS VFR TEXT IFR N0100F200F320")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0825 THIS IS VFR TEXT IFR N0100F200F320",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Speed / level / level following rule change back to GAT
        self.__parse_field_15("N0450M0825 BGH OAT THIS IS OAT TEXT GAT N0100F200F320")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("OAT OAT N0450 M0825 THIS IS OAT TEXT GAT N0100F200F320",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES OAT", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Speed / level / level following rule change back to IFPSTART
        self.__parse_field_15("N0450M0825 BGH IFPSTOP THIS IS OAT TEXT IFPSTART N0100F200F320")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("IFPSTOP IFPS N0450 M0825 THIS IS OAT TEXT IFPSTART N0100F200F320",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFPS", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Speed / level / PLUS following rule change back to IFR
        self.__parse_field_15("N0450M0825 BGH VFR THIS IS VFR TEXT IFR N0100F200PLUS")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0825 THIS IS VFR TEXT IFR N0100F200PLUS",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Speed / level / PLUS following rule change back to GAT
        self.__parse_field_15("N0450M0825 BGH OAT THIS IS OAT TEXT GAT N0100F200PLUS")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("OAT OAT N0450 M0825 THIS IS OAT TEXT GAT N0100F200PLUS",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES OAT", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Speed / level / PLUS following rule change back to IFPSTART
        self.__parse_field_15("N0450M0825 BGH IFPSTOP THIS IS OAT TEXT IFPSTART N0100F200PLUS")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("IFPSTOP IFPS N0450 M0825 THIS IS OAT TEXT IFPSTART N0100F200PLUS",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFPS", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Too long item following rule change back to IFR
        self.__parse_field_15("N0450M0825 BGH VFR THIS IS VFR TEXT IFR ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0825 THIS IS VFR TEXT IFR ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Element 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' is too long for a Field 15 Element",
                         self.__get_error_text_at(0))

        # Too long item following rule change back to GAT
        self.__parse_field_15("N0450M0825 BGH OAT THIS IS OAT TEXT GAT ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("OAT OAT N0450 M0825 THIS IS OAT TEXT GAT ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES OAT", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Element 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' is too long for a Field 15 Element",
                         self.__get_error_text_at(0))

        # Too long item following rule change back to IFPSTART
        self.__parse_field_15("N0450M0825 BGH IFPSTOP THIS IS OAT TEXT IFPSTART ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("IFPSTOP IFPS N0450 M0825 THIS IS OAT TEXT IFPSTART ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFPS", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Element 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' is too long for a Field 15 Element",
                         self.__get_error_text_at(0))

        # STAY time item following rule change back to IFR
        self.__parse_field_15("N0450M0825 BGH VFR THIS IS VFR TEXT IFR STAY5")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0825 THIS IS VFR TEXT IFR STAY5", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # STAY time item following rule change back to GAT
        self.__parse_field_15("N0450M0825 BGH OAT THIS IS OAT TEXT GAT STAY5")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("OAT OAT N0450 M0825 THIS IS OAT TEXT GAT STAY5", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES OAT", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # STAY time item following rule change back to IFPSTART
        self.__parse_field_15("N0450M0825 BGH IFPSTOP THIS IS OAT TEXT IFPSTART STAY5")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("IFPSTOP IFPS N0450 M0825 THIS IS OAT TEXT IFPSTART STAY5",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFPS", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # SID item following rule change back to IFR
        self.__parse_field_15("N0450M0825 BGH VFR THIS IS VFR TEXT IFR SID")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0825 THIS IS VFR TEXT IFR SID", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # SID item following rule change back to GAT
        self.__parse_field_15("N0450M0825 BGH OAT THIS IS OAT TEXT GAT SID")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("OAT OAT N0450 M0825 THIS IS OAT TEXT GAT SID", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES OAT", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # SID item following rule change back to IFPSTART
        self.__parse_field_15("N0450M0825 BGH IFPSTOP THIS IS OAT TEXT IFPSTART SID")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("IFPSTOP IFPS N0450 M0825 THIS IS OAT TEXT IFPSTART SID",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFPS", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # STAR item following rule change back to IFR
        self.__parse_field_15("N0450M0825 BGH VFR THIS IS VFR TEXT IFR STAR")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0825 THIS IS VFR TEXT IFR STAR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # STAR item following rule change back to GAT
        self.__parse_field_15("N0450M0825 BGH OAT THIS IS OAT TEXT GAT STAR")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("OAT OAT N0450 M0825 THIS IS OAT TEXT GAT STAR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES OAT", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # STAR item following rule change back to IFPSTART
        self.__parse_field_15("N0450M0825 BGH IFPSTOP THIS IS OAT TEXT IFPSTART STAR")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("IFPSTOP IFPS N0450 M0825 THIS IS OAT TEXT IFPSTART STAR",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFPS", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Point item following rule change back to IFR
        self.__parse_field_15("N0450M0826 BGH VFR THIS IS VFR TEXT IFR PNT")
        self.assertEqual("ADEP IFR N0450 M0826", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0826", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0826 THIS IS VFR TEXT IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("PNT IFR N0450 M0826", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(4).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting '/SPEED/LEVEL' following 'PNT' to complete rule change to IFR",
                         self.__get_error_text_at(0))

        # Point '/' items following rule change back to IFR
        self.__parse_field_15("N0450M0827 BGH VFR THIS IS VFR TEXT IFR PNT/")
        self.assertEqual("ADEP IFR N0450 M0827", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0827", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0827 THIS IS VFR TEXT IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("PNT IFR N0450 M0827", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(4).unit_test_only())
        self.assertEqual(2, self.ers.get_number_of_errors())
        self.assertEqual("Expecting '/SPEED/LEVEL' following 'PNT' to complete rule change to IFR",
                         self.__get_error_text_at(0))
        self.assertEqual("Field 15 is incomplete, expecting additional data after the final '/'",
                         self.__get_error_text_at(1))

        # Point "Not a '/'" items following rule change back to IFR
        self.__parse_field_15("N0450M0825 BGH VFR THIS IS VFR TEXT IFR PNT ABC")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0825 THIS IS VFR TEXT IFR PNT ABC",
                         self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Something other than a speed / level following Point '/' items following rule change back to IFR
        self.__parse_field_15("N0450M0825 BGH VFR THIS IS VFR TEXT IFR PNT/B9")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0825 THIS IS VFR TEXT IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("PNT IFR N0450 M0825", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(4).unit_test_only())
        self.assertEqual(2, self.ers.get_number_of_errors())
        self.assertEqual("Expecting '/SPEED/LEVEL' following 'PNT' to complete rule change to IFR",
                         self.__get_error_text_at(0))
        self.assertEqual("Expecting SPEED/LEVEL or SPEED/VFR after '/' instead of 'B9'",
                         self.__get_error_text_at(1))

        # Speed / level item following Point '/' items, successful rule change to IFR
        self.__parse_field_15("N0450M0825 BGH VFR THIS IS VFR TEXT IFR PNT/N0100F070")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0825 THIS IS VFR TEXT IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("PNT IFR N0100 F070", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(4).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Speed / VFR item following Point '/' items, successful rule change to IFR and Back to VFR
        self.__parse_field_15("N0450M0825 BGH VFR THIS IS VFR TEXT IFR PNT/N0150VFR")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("BGH IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0825 THIS IS VFR TEXT IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("PNT IFR N0150 F050", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual("VFR VFR N0150 F050", self.ers.get_element_at(4).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(5).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

    def test_point(self):
        # Valid points, all OK
        self.__parse_field_15("N0450M0825 ABC DEF")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("DEF IFR N0450 M0825", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Valid points, LL degrees, all OK
        self.__parse_field_15("N0450M0825 ABC 23N179E")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("23N179E IFR N0450 M0825", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Valid points, LL degrees / minutes all OK
        self.__parse_field_15("N0450M0825 ABC 2314S12356W")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("2314S12356W IFR N0450 M0825", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Valid points, Bearing distance with point in degrees, all OK
        self.__parse_field_15("N0450M0825 ABC 12N123E123456")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("12N123E123456 IFR N0450 M0825", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Valid points, Bearing distance with point in degrees and minutes, all OK
        self.__parse_field_15("N0450M0825 ABC 1234S09012E")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("1234S09012E IFR N0450 M0825", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Invalid LL point, in degrees, error
        self.__parse_field_15("N0450M0825 ABC 91N181E")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("91N181E IFR N0450 M0825", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(2, self.ers.get_number_of_errors())
        self.assertEqual("Latitude degree value must be 0 to 90 instead of '91N181E'",
                         self.__get_error_text_at(0))
        self.assertEqual("Longitude degree value must be 0 to 180 instead of '91N181E'",
                         self.__get_error_text_at(1))

        # Invalid LL point, in degrees, error
        self.__parse_field_15("N0450M0825 ABC 8960N17960E")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("8960N17960E IFR N0450 M0825", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(2, self.ers.get_number_of_errors())
        self.assertEqual("Latitude degree/minute value must be 0 to 9000 with minutes < 60 instead of '8960N17960E'",
                         self.__get_error_text_at(0))
        self.assertEqual("Longitude degree/minute value must be 0 to 18000 with minutes < 60 instead of '8960N17960E'",
                         self.__get_error_text_at(1))

        # Route following a LL point, error
        self.__parse_field_15("N0450M0825 ABC 89N179E B9")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("89N179E IFR N0450 M0825", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("ATS route 'B9' cannot follow a Lat/Long point",
                         self.__get_error_text_at(0))

    def test_dct(self):
        # Truncate following DCT, all OK
        self.__parse_field_15("N0450M0825 ABC DCT T")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("DCT IFR N0450 M0825", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Point following DCT, all OK
        self.__parse_field_15("N0450M0825 ABC DCT DEF")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("DCT IFR N0450 M0825", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("DEF IFR N0450 M0825", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(4).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # "C"" following DCT, all OK
        self.__parse_field_15("N0450M0825 ABC DCT C")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("DCT IFR N0450 M0825", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("C IFR N0450 M0825", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(4).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Something other than above following DCT, error
        self.__parse_field_15("N0450M0829 ABC DCT B9")
        self.assertEqual("ADEP IFR N0450 M0829", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0829", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("DCT IFR N0450 M0829", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("A 'DCT' must be followed by a point instead of 'B9'",
                         self.__get_error_text_at(0))

    def test_stay(self):
        # STAYn with no time, error
        self.__parse_field_15("N0450M0825 ABC STAY4")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting STAY time as '/HHMM' after 'STAY4'",
                         self.__get_error_text_at(0))

        # STAYn '/' with no time, error
        self.__parse_field_15("N0450M0831 ABC STAY4/")
        self.assertEqual("ADEP IFR N0450 M0831", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0831", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Time value as HHMM token missing after '/'",
                         self.__get_error_text_at(0))

        # STAYn '/' followed by something other than a time item, error
        self.__parse_field_15("N0450M0832 ABC STAY4/B9")
        self.assertEqual("ADEP IFR N0450 M0832", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0832", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting HHMM token following STAYx/ element",
                         self.__get_error_text_at(0))

        # STAYn '/' with time + semantic error, error
        self.__parse_field_15("N0450M0833 ABC STAY4/1260")
        self.assertEqual("ADEP IFR N0450 M0833", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0833", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting HHMM token following STAYx/ element",
                         self.__get_error_text_at(0))

        # STAYn '/' with valid time, all OK
        self.__parse_field_15("N0450M0835 ABC STAY4/1259")
        self.assertEqual("ADEP IFR N0450 M0835", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0835", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

    def test_truncate(self):
        # Truncate with something following the "T" - error
        self.__parse_field_15("N0450M0840 ABC T DEF")
        self.assertEqual("ADEP IFR N0450 M0840", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0840", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting end of field 15 after truncation indicator 'T' instead od 'DEF'",
                         self.__get_error_text_at(0))

        # Truncate with nothing following the "T", OK
        self.__parse_field_15("N0450M0841 ABC T")
        self.assertEqual("ADEP IFR N0450 M0841", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0841", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

    def test_cruise_climb_c(self):
        # Cruise Climb, only the 'C' - OK, stored as a point
        self.__parse_field_15("N0450M0840 ABC C")
        self.assertEqual("ADEP IFR N0450 M0840", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0840", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("C IFR N0450 M0840", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Cruise Climb, 'C/' - Error
        self.__parse_field_15("N0450M0841 ABC C/")
        self.assertEqual("ADEP IFR N0450 M0841", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0841", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("C IFR N0450 M0841", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting point / speed / altitude / altitude after start of Cruise/Climb indicator 'C/'",
                         self.__get_error_text_at(0))

        # Cruise Climb, 'C/PNT' - Error
        self.__parse_field_15("N0450M0842 ABC C/PNT")
        self.assertEqual("ADEP IFR N0450 M0842", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0842", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("PNT IFR N0450 M0842", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting point / speed / altitude / altitude after start of Cruise/Climb indicator 'C/PNT'",
                         self.__get_error_text_at(0))

        # Cruise Climb, 'C/PNT/' - Error
        self.__parse_field_15("N0450M0843 ABC C/PNT/")
        self.assertEqual("ADEP IFR N0450 M0843", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0843", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("PNT IFR N0450 M0843", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting speed / altitude / altitude after start of Cruise/Climb indicator 'C/PNT/'",
                         self.__get_error_text_at(0))

        # Cruise Climb, 'C/PNT/N0100F110F220' - OK
        self.__parse_field_15("N0450M0844 ABC C/PNT/N0100F110F220")
        self.assertEqual("ADEP IFR N0450 M0844", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0844", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("PNT IFR N0100 F110", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Cruise Climb, 'C/PNT/N0100F110PLUS' - OK
        self.__parse_field_15("N0450M0845 ABC C/PNT/N0100F110PLUS")
        self.assertEqual("ADEP IFR N0450 M0845", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0845", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("PNT IFR N0100 F110", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Cruise Climb, 'C UNKNOWN' - Error
        self.__parse_field_15("N0450M0846 ABC C UNKNOWN")
        self.assertEqual("ADEP IFR N0450 M0846", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0846", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The element 'UNKNOWN' is an unrecognised Field 15 element",
                         self.__get_error_text_at(0))

        # Cruise Climb, 'C Break Start' - OK
        self.__parse_field_15("N0450M0847 ABC C VFR")
        self.assertEqual("ADEP IFR N0450 M0847", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0847", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("C IFR N0450 M0847", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0847", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual("ADES VFR", self.ers.get_element_at(4).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Cruise Climb, 'C Speed / VFR' - Error
        self.__parse_field_15("N0450M0846 ABC C N0220VFR")
        self.assertEqual("ADEP IFR N0450 M0846", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0846", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting '/' before 'N0220VFR'",
                         self.__get_error_text_at(0))

        # Cruise Climb, 'C Break End' - Error
        self.__parse_field_15("N0450M0846 ABC C GAT")
        self.assertEqual("ADEP IFR N0450 M0846", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0846", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("No OAT section preceding this 'GAT' rule change indicator",
                         self.__get_error_text_at(0))

        # Cruise Climb, 'C DCT' - OK
        self.__parse_field_15("N0450M0846 ABC C DCT")
        self.assertEqual("ADEP IFR N0450 M0846", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0846", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("C IFR N0450 M0846", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("DCT IFR N0450 M0846", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(4).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Cruise Climb, 'C STAYn' - Error
        self.__parse_field_15("N0450M0846 ABC C STAY5")
        self.assertEqual("ADEP IFR N0450 M0846", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0846", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("C IFR N0450 M0846", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting STAY time as '/HHMM' after 'STAY5'",
                         self.__get_error_text_at(0))

        # Cruise Climb, 'C TRUNCATE' - OK
        self.__parse_field_15("N0450M0846 ABC C T")
        self.assertEqual("ADEP IFR N0450 M0846", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0846", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("C IFR N0450 M0846", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Cruise Climb, 'C C' - OK
        self.__parse_field_15("N0450M0846 ABC C C")
        self.assertEqual("ADEP IFR N0450 M0846", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0846", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("C IFR N0450 M0846", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("C IFR N0450 M0846", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(4).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Cruise Climb, 'C PNT' - OK
        self.__parse_field_15("N0450M0846 ABC C PNT")
        self.assertEqual("ADEP IFR N0450 M0846", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0846", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("C IFR N0450 M0846", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("PNT IFR N0450 M0846", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(4).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Cruise Climb, 'C B9' - OK
        self.__parse_field_15("N0450M0846 ABC C B9")
        self.assertEqual("ADEP IFR N0450 M0846", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0846", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("C IFR N0450 M0846", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("B9 IFR N0450 M0846", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(4).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Cruise Climb, 'C SID' - Error
        self.__parse_field_15("N0450M0846 ABC C SID")
        self.assertEqual("ADEP IFR N0450 M0846", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0846", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("C IFR N0450 M0846", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("SID IFR N0450 M0846", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(4).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("SID 'SID' must follow the first SPEED/ALTITUDE and cannot appear anywhere else in field 15",
                         self.__get_error_text_at(0))

        # Cruise Climb, 'C STAR' - Error
        self.__parse_field_15("N0450M0846 ABC C STAR")
        self.assertEqual("ADEP IFR N0450 M0846", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0846", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("C IFR N0450 M0846", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("STAR IFR N0450 M0846", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(4).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Cruise Climb, 'C Speed / Altitude' - Error
        self.__parse_field_15("N0450M0846 ABC C N0330F120")
        self.assertEqual("ADEP IFR N0450 M0846", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0846", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting '/' before 'N0330F120'",
                         self.__get_error_text_at(0))

        # Cruise Climb, 'C Speed / Altitude / Altitude' - Error
        self.__parse_field_15("N0450M0846 ABC C N0200F100F200")
        self.assertEqual("ADEP IFR N0450 M0846", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0846", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting 'C/POINT/' before 'N0200F100F200'",
                         self.__get_error_text_at(0))

        # Cruise Climb, 'C Speed / Altitude / PLUS' - Error
        self.__parse_field_15("N0450M0846 ABC C N0200F100PLUS")
        self.assertEqual("ADEP IFR N0450 M0846", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0846", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting 'C/POINT/' before 'N0200F100PLUS'",
                         self.__get_error_text_at(0))

        # Cruise Climb, 'C To Long' - Error
        self.__parse_field_15("N0450M0846 ABC C ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.assertEqual("ADEP IFR N0450 M0846", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0846", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Element 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' is too long for a Field 15 Element",
                         self.__get_error_text_at(0))

        # Cruise Climb, 'C Stay time' - Error
        self.__parse_field_15("N0450M0846 ABC C 1234")
        self.assertEqual("ADEP IFR N0450 M0846", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0846", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting the keyword 'STAY' before '1234'",
                         self.__get_error_text_at(0))

        # Cruise Climb, 'C LNZ1A' - OK
        self.__parse_field_15("N0450M0846 ABC C LNZ1A")
        self.assertEqual("ADEP IFR N0450 M0846", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0846", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("C IFR N0450 M0846", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("LNZ1A IFR N0450 M0846", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(4).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Cruise Climb, 'C STAR' - OK
        self.__parse_field_15("N0450M0846 ABC C STAR")
        self.assertEqual("ADEP IFR N0450 M0846", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0846", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("C IFR N0450 M0846", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("STAR IFR N0450 M0846", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(4).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

    def test_route(self):
        # Post route, unknown item, Error
        self.__parse_field_15("N0450M0840 ABC B9 UNKNOWN")
        self.assertEqual("ADEP IFR N0450 M0840", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0840", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("B9 IFR N0450 M0840", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The element 'UNKNOWN' is an unrecognised Field 15 element",
                         self.__get_error_text_at(0))

        # Post route, '/' item, Error
        self.__parse_field_15("N0450M0840 ABC B9 /")
        self.assertEqual("ADEP IFR N0450 M0840", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0840", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("B9 IFR N0450 M0840", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting a PRP after an ATS route instead of '/'",
                         self.__get_error_text_at(0))

        # Post route, Break Start item, Error
        self.__parse_field_15("N0450M0840 ABC B9 VFR")
        self.assertEqual("ADEP IFR N0450 M0840", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0840", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("B9 IFR N0450 M0840", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Rule change 'VFR' cannot occur following an ATS route element",
                         self.__get_error_text_at(0))

        # Post route, Speed / VFR item, Error
        self.__parse_field_15("N0450M0840 ABC B9 N0450VFR")
        self.assertEqual("ADEP IFR N0450 M0840", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0840", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("B9 IFR N0450 M0840", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Rule change 'N0450VFR' cannot occur following an ATS route element",
                         self.__get_error_text_at(0))

        # Post route, IFR item, Error
        self.__parse_field_15("N0450M0840 ABC B9 IFR")
        self.assertEqual("ADEP IFR N0450 M0840", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0840", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("B9 IFR N0450 M0840", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("No VFR section preceding this 'IFR' rule change indicator",
                         self.__get_error_text_at(0))

        # Post route, DCT item, Error
        self.__parse_field_15("N0450M0840 ABC B9 DCT")
        self.assertEqual("ADEP IFR N0450 M0840", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0840", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("B9 IFR N0450 M0840", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Cannot go direct ('DCT') from an ATS route element, must be preceded by a point",
                         self.__get_error_text_at(0))

        # Post route, STAYn item, Error
        self.__parse_field_15("N0450M0840 ABC B9 STAY6")
        self.assertEqual("ADEP IFR N0450 M0840", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0840", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("B9 IFR N0450 M0840", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("'STAY6' must be preceded by a point",
                         self.__get_error_text_at(0))

        # Post route, Truncate item, OK
        self.__parse_field_15("N0450M0840 ABC B9 T")
        self.assertEqual("ADEP IFR N0450 M0840", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0840", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("B9 IFR N0450 M0840", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Post route, C item, OK
        self.__parse_field_15("N0450M0840 ABC B9 C")
        self.assertEqual("ADEP IFR N0450 M0840", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0840", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("B9 IFR N0450 M0840", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("C IFR N0450 M0840", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(4).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Post route, Point item, OK
        self.__parse_field_15("N0450M0840 ABC B9 PNT")
        self.assertEqual("ADEP IFR N0450 M0840", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0840", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("B9 IFR N0450 M0840", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("PNT IFR N0450 M0840", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(4).unit_test_only())
        self.assertEqual(0, self.ers.get_number_of_errors())

        # Post route, route item, Error
        self.__parse_field_15("N0450M0840 ABC B9 A17")
        self.assertEqual("ADEP IFR N0450 M0840", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0840", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("B9 IFR N0450 M0840", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Add crossing point between previous ATS route and 'A17'",
                         self.__get_error_text_at(0))

        # Post route, SID / STAR item, Error
        self.__parse_field_15("N0450M0840 ABC B9 LNZ2R")
        self.assertEqual("ADEP IFR N0450 M0840", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0840", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("B9 IFR N0450 M0840", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Add APF between previous ATS route and STAR 'LNZ2R'",
                         self.__get_error_text_at(0))

        # Post route, Speed / Altitude item, Error
        self.__parse_field_15("N0450M0840 ABC B9 N0330F130")
        self.assertEqual("ADEP IFR N0450 M0840", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0840", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("B9 IFR N0450 M0840", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("The SPEED/LEVEL 'N0330F130' cannot follow an ATS route",
                         self.__get_error_text_at(0))

        # Post route, Speed / Altitude / Altitude item, Error
        self.__parse_field_15("N0450M0840 ABC B9 N0330F130F140")
        self.assertEqual("ADEP IFR N0450 M0840", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0840", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("B9 IFR N0450 M0840", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting 'C/POINT/' before 'N0330F130F140'",
                         self.__get_error_text_at(0))

        # Post route, Speed / Altitude / PLUS item, Error
        self.__parse_field_15("N0450M0840 ABC B9 N0330F130PLUS")
        self.assertEqual("ADEP IFR N0450 M0840", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0840", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("B9 IFR N0450 M0840", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting 'C/POINT/' before 'N0330F130PLUS'",
                         self.__get_error_text_at(0))

        # Post route, too long item, Error
        self.__parse_field_15("N0450M0840 ABC B9 ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        self.assertEqual("ADEP IFR N0450 M0840", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0840", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("B9 IFR N0450 M0840", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Element 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' is too long for a Field 15 Element",
                         self.__get_error_text_at(0))

        # Post route, Stay time item, Error
        self.__parse_field_15("N0450M0840 ABC B9 2359")
        self.assertEqual("ADEP IFR N0450 M0840", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0840", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("B9 IFR N0450 M0840", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Expecting the keyword 'STAY' before '2359'",
                         self.__get_error_text_at(0))

        # Post route, SID item, Error
        self.__parse_field_15("N0450M0840 ABC B9 SID")
        self.assertEqual("ADEP IFR N0450 M0840", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0840", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("B9 IFR N0450 M0840", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("SID 'SID' must follow the first SPEED/ALTITUDE and cannot appear anywhere else in field 15",
                         self.__get_error_text_at(0))

        # Post route, STAR item, Error
        self.__parse_field_15("N0450M0840 ABC B9 NOLAN1D")
        self.assertEqual("ADEP IFR N0450 M0840", self.ers.get_first_element().unit_test_only())
        self.assertEqual("ABC IFR N0450 M0840", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("B9 IFR N0450 M0840", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("Add APF between previous ATS route and STAR 'NOLAN1D'",
                         self.__get_error_text_at(0))

    def test_miscellaneous(self):
        # ATS route embedded between lat/long points, Error
        self.__parse_field_15("N0450M0825 00N000E B9 00N001E VFR IFR 00N001W/N0350F100 01N001W 01S001W 02S001W180060")
        self.assertEqual("ADEP IFR N0450 M0825", self.ers.get_first_element().unit_test_only())
        self.assertEqual("00N000E IFR N0450 M0825", self.ers.get_element_at(1).unit_test_only())
        self.assertEqual("00N001E IFR N0450 M0825", self.ers.get_element_at(2).unit_test_only())
        self.assertEqual("VFR VFR N0450 M0825 IFR", self.ers.get_element_at(3).unit_test_only())
        self.assertEqual("00N001W IFR N0350 F100", self.ers.get_element_at(4).unit_test_only())
        self.assertEqual("01N001W IFR N0350 F100", self.ers.get_element_at(5).unit_test_only())
        self.assertEqual("01S001W IFR N0350 F100", self.ers.get_element_at(6).unit_test_only())
        self.assertEqual("02S001W180060 IFR N0350 F100", self.ers.get_element_at(7).unit_test_only())
        self.assertEqual("ADES IFR", self.ers.get_element_at(8).unit_test_only())
        self.assertEqual(1, self.ers.get_number_of_errors())
        self.assertEqual("ATS route 'B9' cannot follow a Lat/Long point",
                         self.__get_error_text_at(0))
        print("Test 01:\n" + self.ers.get_element_at(1).unit_test_only())
        self.ers.print_ers()

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
