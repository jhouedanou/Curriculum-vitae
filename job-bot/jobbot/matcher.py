"""Tri : Claude note chaque offre par rapport au CV."""
from __future__ import annotations

from .config import config, cv, cv_texte
from .llm import LLM
from .models import Note, Offre

SYSTEME = """Tu es un recruteur tech expérimenté en Afrique de l'Ouest francophone.
Tu évalues si une offre d'emploi convient au candidat dont le CV est fourni.

Barème du score (0-100) :
- 85-100 : le poste correspond au cœur du profil (stack, séniorité, type de rôle).
- 70-84  : bonne correspondance, quelques écarts rattrapables.
- 50-69  : correspondance partielle (autre stack principale, rôle voisin).
- 0-49   : ne convient pas.

Méthode (d'après resumeskills · job-description-analyzer, MIT) :
- Liste les exigences principales. Indispensable si l'offre dit « exigé », « requis »,
  si elle figure sous Profil/Prérequis ou revient 3 fois ; souhaitée si « un plus », « idéalement », « apprécié ».
- Une exigence n'est couverte (« oui ») que si le CV la cite explicitement ; proche ou synonyme = « partiel ».
- Le score pèse environ 70 % les indispensables couverts et 30 % les souhaitées.
- Manques : critique = rédhibitoire (diplôme ou licence exigé absent, lieu impossible, expérience
  inférieure de plus de moitié à la demande) ; majeur = à traiter dans la lettre ; mineur = à taire.
  Ne sont PAS rédhibitoires : quelques années d'écart, un diplôme seulement souhaité, un outil
  qui s'apprend, un autre secteur avec des compétences transférables.
- Signaux d'alerte : « polyvalent », « opérationnel immédiatement », « environnement très dynamique »,
  « comme une famille », « salaire attractif » sans chiffre, rémunération 100 % variable, offre vague,
  plusieurs postes en un. Cite les mots de l'offre.
- recommandation : postuler (≥ 75), postuler avec une lettre forte (60-74), pari (50-59), eviter (< 50
  ou un manque critique).
- salaire : recopie l'offre ; n'estime jamais une rémunération.

Règles :
- Le candidat est senior ({annees}+ ans, poste actuel de direction). Un poste junior,
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
    return llm.demander(config()["modeles"]["tri"], SYSTEME.replace("{annees}", str(cv()["annees_experience"])), cv_texte(), consigne, Note, max_tokens=4000)
