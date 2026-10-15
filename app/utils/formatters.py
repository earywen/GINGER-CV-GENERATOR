# -*- coding: utf-8 -*-
import re
from typing import Optional

def compute_initials(name: Optional[str]) -> str:
    """
    Computes official Ginger Burgeap initials from employee full name:
    - Empty/None -> "GB"
    - Single word ("Gaëtan") -> "GA"
    - Two words ("Marine RICHARD") -> "MR"
    - Three words ("Solenn LE BAUD") -> "SLB"
    - Compound names with hyphens ("Jean-Guillaume ROBIN") -> "JGR"
    """
    if not name or not name.strip():
        return "GB"
    parts = [p.strip() for p in name.replace("-", " ").split() if p.strip()]
    if not parts:
        return "GB"
    if len(parts) == 1:
        return parts[0][:2].upper()
    elif len(parts) == 2:
        return (parts[0][0] + parts[1][0]).upper()
    else:
        return "".join(p[0].upper() for p in parts[:3])

def sanitize_filename(name: Optional[str], lang: str = "FR", ext: str = "pdf") -> str:
    """
    Sanitizes employee name and produces a clean, filesystem-safe filename:
    Ex: "Marine RICHARD" -> "CV_Marine_RICHARD_FR.pdf"
    """
    clean_name = (name or "Collaborateur").strip()
    # Replace dangerous path characters with space
    clean_name = re.sub(r'[\\/*?:"<>|]', " ", clean_name)
    # Replace whitespace sequences with single underscore
    clean_name = re.sub(r"\s+", "_", clean_name).strip("_")
    clean_ext = ext.lstrip(".")
    return f"CV_{clean_name}_{lang.upper()}.{clean_ext}"
