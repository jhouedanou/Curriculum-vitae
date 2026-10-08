"""Rédaction : CV adapté, lettre (si demandée) et message court."""
from __future__ import annotations

import re
from typing import Optional

from pydantic import BaseModel

from .config import config, cv, cv_texte
from .llm import LLM
from .models import CVAdapte, Dossier, ExperienceAdaptee, Lettre, Message, Note, Offre
from .sources.base import normaliser

SYSTEME = """Tu prépares la candidature du candidat dont le CV est fourni, pour une offre précise.

RÈGLE ABSOLUE — ZÉRO INVENTION
- Tu reformules, tu choisis et tu réordonnes. Tu n'ajoutes rien.
- Aucun chiffre, outil, diplôme, employeur, client ou projet absent du CV.
- Si l'offre demande une compétence absente du CV, tu ne la cites pas comme acquise.
  Tu peux montrer une compétence proche réellement présente.
- Les noms de compétences et les ids (expériences, projets) sont copiés tels quels depuis le CV.

ADAPTATION AU POSTE
- Reprends les mots-clés de l'offre quand ils décrivent une compétence réelle du CV
  (les logiciels de tri des recruteurs cherchent ces mots).
- Mets en premier ce qui répond aux missions de l'offre.
- Chaque puce : verbe d'action + ce qui a été fait + résultat chiffré si le CV le donne.

STYLE
- Direct et concret. Une idée par phrase.
- Interdit : « passionné », « dynamique », « motivé », « rigoureux », « je me permets »,
  « n'hésitez pas », « véritable », « au sein de », « fort de », « parfaitement »,
  les superlatifs et les formules creuses.
- Parle des besoins de l'entreprise avant de parler du candidat.

LETTRE (seulement si demandée), 250 à 350 mots en 4 paragraphes :
1. Le besoin de l'entreprise tel que l'offre le décrit, et le poste visé.
2. Deux ou trois preuves du CV qui répondent à ce besoin.
3. Ce que le candidat fera dans ses premiers mois à ce poste (déduit des missions de l'offre).
4. Demande d'entretien, en une ou deux phrases.
Pas de formule d'appel ni de signature : le modèle les ajoute.

MESSAGE (email ou message LinkedIn), 80 à 120 mots :
- Première phrase : le poste et ce que le candidat apporte, sans « je me permets ».
- Deux preuves chiffrées du CV.
- Une demande claire (un échange de 15 minutes, un entretien).
- Signature : nom, téléphone, lien du portfolio."""


class _Reponse(BaseModel):
    """Format demandé à Claude (le dossier final est vérifié ensuite)."""
    cv: CVAdapte
    lettre: Optional[Lettre]
    message: Message


def rediger(llm: LLM, offre: Offre, note: Note, avec_lettre: bool) -> Dossier:
    langue = "anglais" if note.langue == "en" else "français"
    consigne = f"""Prépare la candidature pour cette offre. Langue de rédaction : {langue}.
Lettre de motivation : {"OUI, rédige-la" if avec_lettre else "NON, mets lettre à null"}.

<offre>
Titre : {offre.titre}
Entreprise : {note.entreprise or offre.entreprise or "non précisée"}
Lieu : {offre.lieu}
Consignes de candidature : {note.consignes or "aucune"}

{offre.description[:15000]}
</offre>

<analyse>
Points forts : {"; ".join(note.points_forts)}
Écarts : {"; ".join(note.ecarts)}
</analyse>"""
    rep = llm.demander(config()["modeles"]["redaction"], SYSTEME, cv_texte(note.langue), consigne,
                       _Reponse, max_tokens=6000)
    dossier = Dossier(cv=rep.cv, lettre=rep.lettre if avec_lettre else None, message=rep.message)
    return verifier(dossier, note.langue)


# ── Garde-fous : on retire ce qui n'est pas dans le CV ───────────
def verifier(d: Dossier, langue: str = "fr") -> Dossier:
    data = cv(langue)
    noms = [c["nom"] for cat in data["competences"] for c in cat["items"]]
    noms += [t for p in data["projets"] for t in p.get("technos", [])]  # ex. React, Next.js
    norm = {normaliser(n): n for n in noms}

    gardees, retirees = [], []
    for c in d.cv.competences:
        k = normaliser(c)
        trouve = norm.get(k) or (
            next((v for nk, v in norm.items() if nk in k or k in nk), None) if len(k) >= 3 else None
        )
        if trouve:
            if trouve not in gardees:
                gardees.append(trouve)
        else:
            retirees.append(c)
    d.cv.competences = gardees

    ids_exp = [e["id"] for e in data["experiences"]]
    par_id = {e.id: e for e in d.cv.experiences if e.id in ids_exp}
    # Toutes les expériences restent, dans l'ordre du CV. Celles que Claude a oubliées gardent leur texte d'origine.
    d.cv.experiences = [
        par_id.get(e["id"]) or ExperienceAdaptee(id=e["id"], puces=e["realisations"][:3])
        for e in data["experiences"]
    ]

    ids_proj = {p["id"] for p in data["projets"]}
    d.cv.projets = [p for p in d.cv.projets if p in ids_proj][:5]

    d.avertissements = []
    if retirees:
        d.avertissements.append(f"Compétences retirées car absentes du CV : {', '.join(retirees)}")
    d.avertissements += chiffres_suspects(d, langue)
    return d


def chiffres_suspects(d: Dossier, langue: str = "fr") -> list[str]:
    """Signale tout nombre qui n'apparaît pas dans le CV (à vérifier à la main)."""
    connus = set(re.findall(r"\d+", cv_texte(langue)))
    textes = [d.cv.resume, *[p for e in d.cv.experiences for p in e.puces], d.message.texte]
    if d.lettre:
        textes += d.lettre.paragraphes
    alertes = []
    for t in textes:
        for n in re.findall(r"\d+", t):
            if n not in connus:
                alertes.append(f"Chiffre « {n} » absent du CV, dans : « {t[:90]}… »")
    return alertes
