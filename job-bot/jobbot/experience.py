"""Années d'expérience calculées à partir des dates de cv.yaml (rien n'est écrit en dur).

Règle : mois réellement travaillés, un mois couvert par deux postes compte une fois,
arrondi à l'année inférieure. Années par compétence = année en cours − `depuis`.
"""
from __future__ import annotations

import copy
from datetime import date
from typing import Optional


def _mois(texte: str) -> int:
    """« 2019-06 » → numéro de mois absolu."""
    a, m = str(texte).split("-")[:2]
    return int(a) * 12 + int(m) - 1


def periodes(cv: dict) -> list[tuple[str, Optional[str]]]:
    """(début, fin) de chaque poste ; fin None = poste actuel."""
    postes = list(cv.get("experiences", [])) + [x for x in cv.get("experiences_anterieures", []) if isinstance(x, dict)]
    return [(p["debut"], p.get("fin")) for p in postes if p.get("debut")]


def mois_travailles(cv: dict, aujourdhui: Optional[date] = None) -> int:
    aujourdhui = aujourdhui or date.today()
    fin_actuelle = aujourdhui.year * 12 + aujourdhui.month - 1
    mois: set[int] = set()
    for debut, fin in periodes(cv):
        mois.update(range(_mois(debut), (_mois(fin) if fin else fin_actuelle) + 1))
    return len(mois)


def annees_experience(cv: dict, aujourdhui: Optional[date] = None) -> int:
    return mois_travailles(cv, aujourdhui) // 12


def annees_competence(depuis: int, aujourdhui: Optional[date] = None) -> int:
    return max(1, (aujourdhui or date.today()).year - int(depuis))


def completer(cv: dict, aujourdhui: Optional[date] = None) -> dict:
    """Copie du CV prête à afficher : résumé chiffré, `annees` sur chaque compétence,
    anciens postes en texte (comme avant)."""
    d = copy.deepcopy(cv)
    n = annees_experience(cv, aujourdhui)
    d["annees_experience"] = n
    if isinstance(d.get("resume"), str):
        d["resume"] = d["resume"].replace("{annees_experience}", str(n))
    for cat in d.get("competences", []):
        for c in cat.get("items", []):
            if "depuis" in c and "annees" not in c:
                c["annees"] = annees_competence(c["depuis"], aujourdhui)
    d["experiences_anterieures"] = [x["texte"] if isinstance(x, dict) else x for x in d.get("experiences_anterieures", [])]
    return d


def resume_chiffres(cv: dict, aujourdhui: Optional[date] = None) -> str:
    """Ligne ajoutée au YAML lu par Claude : les nombres calculés, pour qu'il les reprenne tels quels."""
    d = completer(cv, aujourdhui)
    comp = ", ".join(f"{c['nom']} {c['annees']}" for cat in d.get("competences", []) for c in cat["items"] if "annees" in c)
    return (f"\n# Calculé le {(aujourdhui or date.today()).isoformat()} : {d['annees_experience']} ans d'expérience au total."
            f"\n# Années par compétence : {comp}.\n")
