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

ADAPTATION AU POSTE (d'après resumeskills · resume-tailor, resume-ats-optimizer, tech-resume-optimizer, MIT)
- Reprends les mots-clés de l'offre quand ils décrivent une compétence réelle du CV
  (les logiciels de tri des recruteurs cherchent ces mots). Utilise le terme exact de l'offre quand
  le CV décrit la même chose avec un autre mot, sans jamais changer le sens.
- Un mot-clé essentiel revient 2 à 4 fois (profil, compétences, expériences) ; pas de bourrage,
  varie les formes (« pilotage d'équipe » / « piloté l'équipe »).
- Titre et profil reprennent l'intitulé du poste si le CV le justifie, avec 5 à 8 mots-clés de l'offre
  réellement présents dans le CV.
- Compétences : en tête, celles qui répondent aux premières exigences de l'offre. Pas de bureautique
  ni d'OS sauf si l'offre les demande.
- Mets en premier ce qui répond aux missions de l'offre. La première puce de chaque poste répond
  à une exigence clé.
- Chaque puce : verbe d'action + ce qui a été fait + technologie + résultat chiffré si le CV le donne.
  Une ou deux lignes. Jamais « responsable de », « a participé à », « a aidé à ».
- Ne change aucun chiffre ni intitulé de poste. « A travaillé avec » ne devient pas « a dirigé ».
- Techno exigée absente du CV : cite seulement la proche réellement présente (Vue.js pour une offre React).
- a_completer : pour 2 à 5 puces importantes SANS résultat chiffré dans le CV, pose au candidat la question
  qui permettrait de le chiffrer (« Combien d'utilisateurs pour X ? »). Ne complète jamais toi-même.

STYLE
- Direct et concret. Une idée par phrase.
- Interdit : « passionné », « dynamique », « motivé », « rigoureux », « je me permets »,
  « n'hésitez pas », « véritable », « au sein de », « fort de », « parfaitement »,
  les superlatifs et les formules creuses.
- Parle des besoins de l'entreprise avant de parler du candidat.

LETTRE (seulement si demandée), 250 à 350 mots en 4 paragraphes (d'après resumeskills · cover-letter-generator) :
1. Le besoin de l'entreprise tel que l'offre le décrit, et le poste visé. N'ouvre pas par « Je »,
   ni par « Je vous écris pour », « Suite à votre annonce », « Je suis le candidat idéal ».
2. Leur besoin principal + l'expérience exacte du CV qui y répond + le résultat s'il est dans le CV.
3. Ce que le candidat fera dans ses premiers mois (déduit des missions), et le manque majeur de l'analyse
   traité sans s'excuser, par une compétence voisine réelle. Aucune formation « en cours » inventée.
4. Demande d'échange explicite, liée à un élément précis de l'offre. Pas de « Veuillez trouver ci-joint »,
   ni de « Je reste à votre disposition ».
- Surqualifié : explique la motivation (rôle plus opérationnel, impact direct).
- Destinataire inconnu : « Service Recrutement — Entreprise », jamais « À qui de droit ».
- Ton plus formel pour une banque, une institution ou une ONG ; plus direct pour une startup ou une agence.
Pas de formule d'appel ni de signature : le modèle les ajoute.

MESSAGE (email ou message LinkedIn), 80 à 120 mots (d'après resumeskills · cold-email-writer) :
- Ton d'un pair qui fait un constat, pas d'une mini-lettre. Supprime toute phrase qui irait à n'importe quelle entreprise.
- Première phrase : un élément précis de l'offre et le poste, sans « je me permets »,
  ni « votre mission me parle ».
- Le lien en constat : « Vous cherchez X ; c'est ce que je fais chez Y ». Une ou deux preuves du CV
  (chiffrées si le CV le donne), pas une liste de réalisations.
- Une demande claire et sans pression (un échange de 15 minutes). Pas de « Dans l'attente »,
  ni de « J'aimerais avoir l'opportunité ».
- Objet : respecte les consignes de l'offre ; sinon « Candidature — intitulé du poste — Prénom Nom ».
- Signature : nom, téléphone, lien du portfolio."""


class _Reponse(BaseModel):
    """Format demandé à Claude (le dossier final est vérifié ensuite)."""
    cv: CVAdapte
    lettre: Optional[Lettre]
    message: Message
    a_completer: list[str]


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
Arguments les plus forts : {"; ".join(note.arguments_forts) or "—"}
Écarts : {"; ".join(note.ecarts)}
Manques à traiter : {"; ".join(f"{m.intitule} ({m.gravite})" for m in note.manques if m.gravite != "mineur") or "—"}
Mots-clés de l'offre absents du CV (ne pas les revendiquer) : {", ".join(note.mots_cles_absents) or "—"}
Surqualification : {"oui" if note.surqualification else "non"}
</analyse>"""
    rep = llm.demander(config()["modeles"]["redaction"], SYSTEME, cv_texte(note.langue), consigne,
                       _Reponse, max_tokens=6000)
    dossier = Dossier(cv=rep.cv, lettre=rep.lettre if avec_lettre else None, message=rep.message,
                      a_completer=rep.a_completer)
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
