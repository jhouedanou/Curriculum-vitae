"""Lecture des dates écrites librement dans les offres (« 30/10/2026 », « 30 octobre 2026 »…)."""
from __future__ import annotations

import re
from datetime import date
from typing import Optional

from .sources.base import normaliser

MOIS = {
    "janvier": 1, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6, "juillet": 7,
    "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12,
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6, "july": 7,
    "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "fev": 2, "mar": 3, "apr": 4, "avr": 4, "jun": 6, "jul": 7, "juil": 7,
    "aug": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _annee(a: str) -> int:
    n = int(a)
    return n + 2000 if n < 100 else n


def _faire(a: int, m: int, j: int) -> Optional[date]:
    try:
        return date(a, m, j)
    except ValueError:
        return None


def lire_date(texte: Optional[str]) -> Optional[date]:
    """Renvoie la date trouvée dans le texte, ou None si rien de sûr."""
    if not texte:
        return None
    t = normaliser(texte)
    if m := re.search(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b", t):
        return _faire(int(m[1]), int(m[2]), int(m[3]))
    if m := re.search(r"\b(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{2,4})\b", t):
        return _faire(_annee(m[3]), int(m[2]), int(m[1]))
    if m := re.search(r"\b(\d{1,2})(?:er)?\s+([a-z]+)\.?\s+(\d{4})\b", t):
        if m[2] in MOIS:
            return _faire(int(m[3]), MOIS[m[2]], int(m[1]))
    if m := re.search(r"\b([a-z]+)\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\b", t):
        if m[1] in MOIS:
            return _faire(int(m[3]), MOIS[m[1]], int(m[2]))
    return None


def expiree(date_limite: Optional[str], aujourdhui: Optional[date] = None) -> bool:
    d = lire_date(date_limite)
    return bool(d and d < (aujourdhui or date.today()))
