"""Lire une offre à partir de son adresse : une seule page, à la demande de l'utilisateur."""
from __future__ import annotations

import ipaddress
import re
from typing import Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from .sources.base import Http, html_vers_texte

# Sites qui interdisent la lecture automatique ou la bloquent (mur de connexion).
SITES_A_COLLER = ("linkedin.com", "indeed.com", "indeed.fr", "emploibenin.com", "glassdoor.com", "glassdoor.fr")
TEXTE_MIN = 300


class LienIllisible(Exception):
    """Le lien ne donne pas une offre lisible. Le message s'adresse à l'utilisateur."""


def verifier_lien(url: str) -> str:
    """Renvoie l'adresse nettoyée, ou lève LienIllisible avec la raison."""
    url = (url or "").strip()
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.hostname:
        raise LienIllisible("Ce n'est pas une adresse web complète : elle doit commencer par https://")
    hote = p.hostname.lower()
    if hote == "localhost" or hote.endswith(".local"):
        raise LienIllisible("Cette adresse désigne cet ordinateur, pas un site d'offres.")
    try:
        ip = ipaddress.ip_address(hote)
    except ValueError:
        ip = None
    if ip and (ip.is_private or ip.is_loopback or ip.is_link_local):
        raise LienIllisible("Cette adresse désigne un réseau privé, pas un site d'offres.")
    if any(hote == s or hote.endswith("." + s) for s in SITES_A_COLLER):
        raise LienIllisible(f"{hote} n'autorise pas la lecture automatique. Copie le texte de l'annonce "
                            "et colle-le dans le champ « Texte de l'offre ».")
    return url


def _titre(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for attr in ({"property": "og:title"}, {"name": "twitter:title"}):
        m = soup.find("meta", attrs=attr)
        if m and m.get("content", "").strip():
            return m["content"].strip()
    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        return h1.get_text(" ", strip=True)
    return soup.title.get_text(" ", strip=True) if soup.title else ""


def lire_offre(url: str, http: Optional[Http] = None) -> tuple[str, str]:
    """Télécharge la page et renvoie (titre, texte de l'offre)."""
    url = verifier_lien(url)
    try:
        html = (http or Http()).get(url).text
    except LienIllisible:
        raise
    except Exception as err:
        raise LienIllisible(f"Page inaccessible ({err}). Colle le texte de l'annonce à la place.") from err
    texte = html_vers_texte(html)
    if len(texte) < TEXTE_MIN:
        raise LienIllisible("La page ne contient pas assez de texte lisible : l'annonce s'affiche sans doute "
                            "après connexion ou par JavaScript. Colle le texte de l'annonce à la place.")
    titre = re.sub(r"\s+", " ", _titre(html))[:120]
    if not titre:
        titre = next((l.strip() for l in texte.splitlines() if l.strip()), "Offre")[:120]
    return titre, texte
