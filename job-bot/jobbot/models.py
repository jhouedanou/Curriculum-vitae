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
# Méthode d'analyse inspirée de resumeskills (job-description-analyzer, resume-ats-optimizer), MIT.
class Exigence(BaseModel):
    intitule: str = Field(description="Exigence de l'offre, en quelques mots")
    indispensable: bool = Field(description="true si exigée/requise ; false si « un plus », « idéalement »")
    couvert: Literal["oui", "partiel", "non"] = Field(description="oui = cité tel quel dans le CV ; partiel = proche")
    preuve_cv: Optional[str] = Field(description="Où le CV le montre (poste, projet), sinon null")


class Manque(BaseModel):
    intitule: str
    gravite: Literal["critique", "majeur", "mineur"] = Field(
        description="critique = rédhibitoire ; majeur = à traiter dans la lettre ; mineur = ne pas en parler")
    strategie: str = Field(description="Comment y répondre avec une compétence voisine réelle du CV")


class Note(BaseModel):
    score: int = Field(description="Adéquation candidat / offre, de 0 à 100")
    verdict: str = Field(description="Une phrase qui résume le score")
    recommandation: Literal["postuler", "postuler avec une lettre forte", "pari", "eviter"]
    points_forts: list[str] = Field(description="2 à 4 raisons concrètes, tirées du CV")
    ecarts: list[str] = Field(description="Ce qui manque ou ne colle pas (niveau, techno, secteur…)")
    exigences: list[Exigence] = Field(description="Les 4 à 10 exigences principales de l'offre")
    manques: list[Manque] = Field(description="Les écarts classés par gravité")
    mots_cles_absents: list[str] = Field(description="Mots-clés importants de l'offre absents du CV")
    arguments_forts: list[str] = Field(description="Les 3 arguments du CV les plus forts pour cette offre")
    signaux: list[str] = Field(description="Signaux d'alerte de l'offre (charge, flou, salaire caché…), cités")
    surqualification: bool = Field(description="Le candidat est-il nettement au-dessus du poste ?")
    seniorite: Literal["junior", "confirme", "senior", "lead", "direction", "inconnu"]
    type_contrat: Optional[str] = Field(description="CDI, CDD, freelance, consultance… si l'offre le dit")
    mode_travail: Literal["sur site", "hybride", "teletravail", "inconnu"]
    salaire: Optional[str] = Field(description="Rémunération telle qu'écrite dans l'offre, sinon null. Jamais d'estimation")
    entreprise: Optional[str] = Field(description="Nom de l'entreprise si l'offre le donne")
    intitule: str = Field(description="Intitulé exact du poste")
    langue: Literal["fr", "en"] = Field(description="Langue de l'offre")
    lettre_demandee: bool = Field(description="L'offre demande-t-elle une lettre de motivation ?")
    email_candidature: Optional[str] = Field(description="Adresse email où envoyer la candidature, si donnée")
    date_limite: Optional[str] = Field(description="Date limite de candidature, si donnée")
    consignes: Optional[str] = Field(description="Consignes de candidature (objet du mail, pièces à joindre…)")
    alerte: Optional[str] = Field(description="Signal d'arnaque (frais demandés, etc.), sinon null")


# Valeurs par défaut pour relire les notes enregistrées avant l'ajout de ces champs.
NOTE_DEFAUTS = dict(recommandation="pari", exigences=[], manques=[], mots_cles_absents=[], arguments_forts=[],
                    signaux=[], surqualification=False, seniorite="inconnu", type_contrat=None,
                    mode_travail="inconnu", salaire=None)


def lire_note(json_texte: str) -> Note:
    import json
    return Note.model_validate({**NOTE_DEFAUTS, **json.loads(json_texte)})


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
    a_completer: list[str] = []      # questions au candidat : résultats non chiffrés dans le CV
    avertissements: list[str] = []   # rempli par les garde-fous, pas par Claude


# ── Préparation d'entretien et relance (coach.py) ────────────
# D'après resumeskills (interview-prep-generator, salary-negotiation-prep, cold-email-writer), MIT.
class TrameSTAR(BaseModel):
    situation: str
    tache: str
    action: str
    resultat: str = Field(description="Résultat tiré du CV, ou « non chiffré dans le CV — à préciser »")
    experience_source: str = Field(description="Poste et employeur du CV d'où vient l'exemple")


class QuestionProbable(BaseModel):
    question: str
    categorie: Literal["comportementale", "technique", "standard", "motivation"]
    probabilite: Literal["haute", "moyenne"]
    star: Optional[TrameSTAR] = Field(description="null si aucune expérience du CV ne convient")
    conseil: Optional[str] = Field(description="Une phrase : ce que le recruteur veut entendre")


class PointFaible(BaseModel):
    manque: str
    question_piege: str
    reponse: str = Field(description="Réponse honnête, appuyée sur une compétence voisine réelle")


class Salaire(BaseModel):
    fourchette_offre: Optional[str] = Field(description="Telle qu'écrite dans l'offre, sinon null")
    strategie: str
    arguments: list[str] = Field(description="Arguments de valeur tirés du CV")
    negociable: list[str] = Field(description="Éléments hors salaire fixe à négocier")
    phrases: list[str] = Field(description="2 ou 3 phrases prêtes à dire")


class PreparationEntretien(BaseModel):
    competences_evaluees: list[str] = Field(description="3 à 6 compétences, chacune avec la phrase de l'offre")
    pitch: str = Field(description="« Présentez-vous » en 2 minutes, orienté vers l'offre")
    questions: list[QuestionProbable] = Field(description="8 à 12 questions probables")
    points_faibles: list[PointFaible]
    questions_a_poser: list[str] = Field(description="5 à 7 questions ouvertes à poser au recruteur")
    salaire: Salaire
    a_eviter: list[str]
    a_verifier: list[str] = Field(description="Infos manquantes à demander au candidat avant l'entretien")


class Relance(BaseModel):
    objet: str
    texte: str = Field(description="60 à 110 mots, signature incluse")
    element_nouveau: str = Field(description="Ce que la relance apporte de neuf par rapport au premier message")
