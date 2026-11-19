"""Novojob Côte d'Ivoire — flux RSS officiel du site."""
from __future__ import annotations

import re
from typing import Iterator

import feedparser

from ..models import Offre
from .base import Source, fragment_vers_texte, html_vers_texte

RSS_DEFAUT = "https://www.novojob.com/cote-d-ivoire/rss"


class Novojob(Source):
    nom = "novojob"

    def offres(self) -> Iterator[Offre]:
        flux = self.conf.get("rss", RSS_DEFAUT)
        for url in [flux] if isinstance(flux, str) else flux:  # un flux par pays
            try:
                r = self.http.get(url)
            except Exception as err:
                print(f"  ! novojob {url} : {err}")
                continue
            yield from lire_flux(r.content)

    def completer(self, o: Offre) -> Offre:
        if len(o.description) >= 600 or not o.url:
            return o
        page = self.http.get(o.url)
        texte = html_vers_texte(page.text)
        if len(texte) > len(o.description):
            o.description = texte
        return o


def lire_flux(contenu: bytes | str) -> Iterator[Offre]:
    flux = feedparser.parse(contenu)
    for e in flux.entries:
        lien = e.get("link", "")
        m = re.search(r"/(\d+)-[^/]*$", lien)
        ref = m.group(1) if m else (e.get("id") or lien)
        # …/offre-d-emploi/cote-d-ivoire/abidjan/136879-… → « Abidjan »
        # …/offre-d-emploi/benin/cotonou/1234-… → pays et ville
        m_pays = re.search(r"novojob\.com/([a-z-]+)/", lien)
        pays = {"cote-d-ivoire": "Côte d'Ivoire", "benin": "Bénin"}.get(m_pays.group(1) if m_pays else "", "Côte d'Ivoire")
        lieu = ""
        m_lieu = re.search(r"/offre-d-emploi/[a-z-]+/([a-z-]+)/\d+-", lien)
        if m_lieu:
            lieu = m_lieu.group(1).replace("-", " ").title()
        yield Offre(
            source="novojob",
            ref=str(ref),
            titre=(e.get("title") or "").strip().lstrip(":").strip(),
            url=lien,
            lieu=lieu or pays,
            publie_le=e.get("published", ""),
            description=fragment_vers_texte(e.get("description", "")),
        )
