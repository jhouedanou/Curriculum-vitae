"""Outils communs aux sources : HTTP poli, texte propre, pré-filtre."""
from __future__ import annotations

import re
import time
import unicodedata
from typing import Iterable, Iterator

import httpx
from bs4 import BeautifulSoup

from ..config import config
from ..models import Offre


class Http:
    """Client HTTP qui attend entre deux requêtes (on reste poli avec les sites)."""

    def __init__(self) -> None:
        conf = config().get("http", {})
        self.delai = float(conf.get("delai_entre_requetes", 2))
        self._derniere = 0.0
        self.client = httpx.Client(
            headers={"User-Agent": conf.get("user_agent", "JobBot personnel")},
            timeout=30,
            follow_redirects=True,
        )

    ESSAIS = 3

    def get(self, url: str, **kw) -> httpx.Response:
        """GET poli. Réessaie 2 fois (attente croissante) si le réseau coupe ou si le site sature."""
        for essai in range(self.ESSAIS):
            attente = self.delai * (2 ** essai) - (time.monotonic() - self._derniere)
            if attente > 0:
                time.sleep(attente)
            try:
                r = self.client.get(url, **kw)
                if r.status_code in (429, 500, 502, 503, 504) and essai < self.ESSAIS - 1:
                    continue
                r.raise_for_status()
                return r
            except httpx.TransportError:
                if essai == self.ESSAIS - 1:
                    raise
            finally:
                self._derniere = time.monotonic()
        raise RuntimeError("inaccessible")  # jamais atteint


def normaliser(texte: str) -> str:
    """Minuscules, sans accents : « Développeur » → « developpeur »."""
    t = unicodedata.normalize("NFKD", texte or "")
    return "".join(c for c in t if not unicodedata.combining(c)).lower()


def _contient(texte: str, mots: Iterable[str]) -> bool:
    for mot in mots:
        m = re.escape(normaliser(mot))
        if re.search(rf"(?<![a-z0-9]){m}(?![a-z0-9])", texte):
            return True
    return False


def passe_le_filtre(o: Offre) -> bool:
    """Pré-filtre gratuit avant l'IA (voir config.yaml → filtre)."""
    f = config().get("filtre", {})
    texte = normaliser(f"{o.titre}\n{o.description}")
    titre = normaliser(o.titre)
    if _contient(titre, f.get("exclure", [])):
        return False
    return _contient(texte, f.get("inclure", []))


def html_vers_texte(html: str) -> str:
    """Garde le texte utile d'une page (sans menus ni pubs)."""
    try:
        import trafilatura

        texte = trafilatura.extract(html, include_links=False, include_tables=True, favor_recall=True)
        if texte and len(texte) > 200:
            return texte.strip()
    except Exception:
        pass
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form", "noscript"]):
        tag.decompose()
    lignes = (l.strip() for l in soup.get_text("\n").splitlines())
    return "\n".join(l for l in lignes if l)


def fragment_vers_texte(html: str) -> str:
    """Pour un petit bout de HTML (ex. : description RSS)."""
    soup = BeautifulSoup(html or "", "html.parser")
    for br in soup.find_all(["br", "p", "li", "div"]):
        br.insert_after("\n")
    lignes = (l.strip() for l in soup.get_text().splitlines())
    return "\n".join(l for l in lignes if l)


class Source:
    """Une source d'offres. Chaque source renvoie des Offre (nouvelles ou non)."""

    nom = "source"

    def __init__(self, http: Http, conf: dict):
        self.http = http
        self.conf = conf

    def offres(self) -> Iterator[Offre]:
        raise NotImplementedError

    def completer(self, o: Offre) -> Offre:
        """Récupère la description complète si besoin (appelée seulement si le titre passe le filtre)."""
        return o
