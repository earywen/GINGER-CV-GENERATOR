# -*- coding: utf-8 -*-
import pytest
from app.utils.formatters import compute_initials

@pytest.mark.parametrize("name,expected", [
    ("", "GB"),
    (None, "GB"),
    ("   ", "GB"),
    ("Gaëtan", "GA"),
    ("Marine RICHARD", "MR"),
    ("Etienne LANGARD", "EL"),
    ("Jean-Guillaume ROBIN", "JGR"),
    ("Solenn LE BAUD", "SLB"),
    ("Luis CAVALCANTE FRAGA", "LCF"),
    ("Marie-Anne DE LA TOUR", "MAD"),
])
def test_compute_initials(name, expected):
    assert compute_initials(name) == expected
