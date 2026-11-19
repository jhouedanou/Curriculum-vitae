"""Tri : Claude note chaque offre par rapport au CV."""
from __future__ import annotations

from .config import config, cv_texte
from .llm import LLM
from .models import Note, Offre

SYSTEME = """Tu es un recruteur tech expérimenté en Afrique de l'Ouest francophone.
Tu évalues si une offre d'emploi convient au candidat dont le CV est fourni.

Barème du score (0-100) :
- 85-100 : le poste correspond au cœur du profil (stack, séniorité, type de rôle).
- 70-84  : bonne correspondance, quelques écarts rattrapables.
- 50-69  : correspondance partielle (autre stack principale, rôle voisin).
- 0-49   : ne convient pas.

Règles :
- Le candidat est senior (12+ ans, poste actuel de direction). Un poste junior,
  d'assistant ou de stagiaire est sous-qualifié pour lui : score de 40 maximum.
- Un poste sans lien avec le web, le digital, le design ou la gestion de projet tech : 20 maximum.
- Points forts et écarts : uniquement des faits présents dans le CV ou dans l'offre.
- lettre_demandee = true seulement si l'offre cite une lettre de motivation
  (ou « cover letter », « LM », « CV + lettre »).
- alerte : signale toute demande d'argent (frais de dossier, de formation, de
  visite médicale payés au recruteur…). Sinon null.
- Phrases courtes, en français."""


def noter(llm: LLM, offre: Offre) -> Note:
    consigne = f"""Note cette offre pour le candidat.

<offre>
Titre : {offre.titre}
Entreprise : {offre.entreprise or "non précisée"}
Lieu : {offre.lieu}
Publiée le : {offre.publie_le or "?"}
Lien : {offre.url}

{offre.description[:12000] or "(pas de description : juge sur le titre et sois prudent)"}
</offre>"""
    return llm.demander(config()["modeles"]["tri"], SYSTEME, cv_texte(), consigne, Note, max_tokens=1500)
