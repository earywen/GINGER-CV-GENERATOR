# -*- coding: utf-8 -*-
import unittest
from app.services.image_processor import compute_initials

class TestInitialsParity(unittest.TestCase):
    def test_empty_or_none(self):
        self.assertEqual(compute_initials(""), "GB")
        self.assertEqual(compute_initials(None), "GB")

    def test_single_word(self):
        self.assertEqual(compute_initials("Gaëtan"), "GA")

    def test_two_words(self):
        self.assertEqual(compute_initials("Marine RICHARD"), "MR")
        self.assertEqual(compute_initials("Etienne LANGARD"), "EL")

    def test_hyphenated_names(self):
        # Jean-Guillaume ROBIN -> parts: ["Jean", "Guillaume", "ROBIN"] -> JGR
        self.assertEqual(compute_initials("Jean-Guillaume ROBIN"), "JGR")

    def test_three_words(self):
        self.assertEqual(compute_initials("Solenn LE BAUD"), "SLB")
        self.assertEqual(compute_initials("Luis CAVALCANTE FRAGA"), "LCF")

if __name__ == "__main__":
    unittest.main()
