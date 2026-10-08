"""Formats de données du bot (offres, notes, dossiers)."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


# ── Offre d'emploi ───────────────────────────────────────────
class Offre(BaseModel):
    source: str                      # novojob, educarriere, remotive, manuel
    ref: str                         # identifiant unique chez la source
    titre: str
    url: str = ""
    entreprise: str = ""
    lieu: str = ""
    publie_le: str = ""
    description: str = ""            # texte brut de l'offre
    id: Optional[int] = None         # numéro interne (base SQLite)


# ── Résultat du tri (renvoyé par Claude) ─────────────────────
class Note(BaseModel):
    score: int = Field(description="Adéquation candidat / offre, de 0 à 100")
    verdict: str = Field(description="Une phrase qui résume le score")
    points_forts: list[str] = Field(description="2 à 4 raisons concrètes, tirées du CV")
    ecarts: list[str] = Field(description="Ce qui manque ou ne colle pas (niveau, techno, secteur…)")
    entreprise: Optional[str] = Field(description="Nom de l'entreprise si l'offre le donne")
    intitule: str = Field(description="Intitulé exact du poste")
    langue: Literal["fr", "en"] = Field(description="Langue de l'offre")
    lettre_demandee: bool = Field(description="L'offre demande-t-elle une lettre de motivation ?")
    email_candidature: Optional[str] = Field(description="Adresse email où envoyer la candidature, si donnée")
    date_limite: Optional[str] = Field(description="Date limite de candidature, si donnée")
    consignes: Optional[str] = Field(description="Consignes de candidature (objet du mail, pièces à joindre…)")
    alerte: Optional[str] = Field(description="Signal d'arnaque (frais demandés, etc.), sinon null")


# ── Dossier de candidature (renvoyé par Claude) ──────────────
class ExperienceAdaptee(BaseModel):
    id: str = Field(description="id de l'expérience dans le CV")
    puces: list[str] = Field(description="2 à 4 réalisations reformulées pour ce poste")


class CVAdapte(BaseModel):
    titre: str = Field(description="Titre du CV aligné sur le poste visé")
    resume: str = Field(description="Profil de 3 à 4 phrases")
    competences: list[str] = Field(description="8 à 12 compétences du CV, la plus pertinente d'abord")
    experiences: list[ExperienceAdaptee] = Field(description="Toutes les expériences du CV, dans l'ordre du CV")
    projets: list[str] = Field(description="ids de 3 à 5 projets du CV les plus utiles pour ce poste")


class Lettre(BaseModel):
    objet: str
    destinataire: str = Field(description="Ex. : « Service Recrutement — Nom de l'entreprise »")
    paragraphes: list[str] = Field(description="4 paragraphes, sans formule d'appel ni signature")


class Message(BaseModel):
    objet_email: str
    texte: str = Field(description="Message court et percutant, 80 à 120 mots, signature incluse")


class Dossier(BaseModel):
    cv: CVAdapte
    lettre: Optional[Lettre] = None
    message: Message
    avertissements: list[str] = []   # rempli par les garde-fous, pas par Claude
