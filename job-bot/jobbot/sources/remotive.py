"""Remotive — API publique d'offres 100 % remote.

Conditions de Remotive : 4 appels par jour maximum, garder le lien
vers l'offre Remotive et citer Remotive comme source. Le bot ne
l'appelle donc qu'une fois toutes les 6 heures.
"""
from __future__ import annotations

from typing import Iterator

from ..models import Offre
from .base import Source, fragment_vers_texte, normaliser

API = "https://remotive.com/api/remote-jobs"
INTERVALLE_MIN = 6 * 3600  # secondes


class Remotive(Source):
    nom = "remotive"

    def offres(self) -> Iterator[Offre]:
        params = {"category": self.conf.get("categorie", "software-dev"), "limit": 150}
        data = self.http.get(API, params=params).json()
        yield from lire_json(data, self.conf.get("lieux_acceptes", []))


def lire_json(data: dict, lieux_acceptes: list[str]) -> Iterator[Offre]:
    zones = [normaliser(z) for z in lieux_acceptes]
    for j in data.get("jobs", []):
        lieu = j.get("candidate_required_location") or ""
        if zones and not any(z in normaliser(lieu) for z in zones):
            continue
        yield Offre(
            source="remotive",
            ref=str(j.get("id")),
            titre=j.get("title", "").strip(),
            url=j.get("url", ""),
            entreprise=j.get("company_name", ""),
            lieu=f"Remote ({lieu})" if lieu else "Remote",
            publie_le=j.get("publication_date", ""),
            description=fragment_vers_texte(j.get("description", ""))
            + (f"\n\nSalaire : {j['salary']}" if j.get("salary") else "")
            + "\n\nSource : Remotive",
        )
