"""Educarrière (emploi.educarriere.ci) — lecture de la liste des offres.

Le site n'a pas de flux RSS : on lit la page HTML, doucement
(1 requête toutes les 2 s, quelques pages par jour seulement).
"""
from __future__ import annotations

import re
from typing import Iterator
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ..models import Offre
from .base import Source, html_vers_texte

BASE_URL = "https://emploi.educarriere.ci/"
LIEN_OFFRE = re.compile(r"offre-(\d+)-([a-z0-9-]+)\.html", re.I)


class Educarriere(Source):
    nom = "educarriere"

    def offres(self) -> Iterator[Offre]:
        vues: set[str] = set()
        for n in range(1, int(self.conf.get("pages", 2)) + 1):
            url = BASE_URL if n == 1 else urljoin(BASE_URL, f"page/all?page={n}")
            try:
                html = self.http.get(url).text
            except Exception as err:  # une page en panne ne bloque pas les autres
                print(f"  ! educarriere page {n} : {err}")
                break
            nouvelles = 0
            for o in lire_liste(html):
                if o.ref not in vues:
                    vues.add(o.ref)
                    nouvelles += 1
                    yield o
            if nouvelles == 0:
                break

    def completer(self, o: Offre) -> Offre:
        page = self.http.get(o.url)
        o.description = html_vers_texte(page.text)
        return o


def lire_liste(html: str) -> Iterator[Offre]:
    soup = BeautifulSoup(html, "html.parser")
    deja: set[str] = set()
    for a in soup.find_all("a", href=LIEN_OFFRE):
        m = LIEN_OFFRE.search(a["href"])
        ref, slug = m.group(1), m.group(2)
        titre = " ".join(a.get_text(" ").split())
        if ref in deja:
            continue
        # Un même lien peut apparaître sur l'image et sur le titre : on garde celui qui a du texte.
        if not titre or titre.lower() in {"postuler", "voir l'offre", "lire la suite", "voir plus"}:
            titre = slug.replace("-", " ").upper()
        deja.add(ref)
        yield Offre(
            source="educarriere",
            ref=ref,
            titre=titre,
            url=urljoin(BASE_URL, a["href"]),
            lieu="Côte d'Ivoire",
        )
