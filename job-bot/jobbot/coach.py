"""Après l'envoi : préparation d'entretien et relance.

Prompts adaptés de resumeskills (interview-prep-generator, salary-negotiation-prep,
cold-email-writer) — https://github.com/paramchoudhary/resumeskills, MIT,
Copyright (c) 2026 Resume Skills. Voir NOTICE.md.
"""
from __future__ import annotations

from .config import config, cv_texte
from .llm import LLM
from .models import Note, Offre, PreparationEntretien, Relance

SYSTEME_ENTRETIEN = """Tu prépares le candidat dont le CV est fourni (développeur web senior, chef de projet
digital, Abidjan) à un entretien pour l'offre donnée.

RÈGLE ABSOLUE — ZÉRO INVENTION
- Chaque situation, action, résultat, chiffre, outil ou employeur vient du CV.
- Résultat non chiffré dans le CV : écris « non chiffré dans le CV — à préciser » et ajoute la question
  dans a_verifier.
- Aucun chiffre de marché, aucun salaire, aucun fait sur l'entreprise absent de l'offre.

À PRODUIRE
1. competences_evaluees : 3 à 6, chacune suivie de la phrase de l'offre qui la justifie.
2. pitch : « Présentez-vous » en 2 minutes environ, orienté vers les missions de l'offre.
3. questions : 8 à 12, comportementales (leadership, problème résolu, collaboration, échec),
   techniques (stack de l'offre) et standards (« Pourquoi ce poste ? », « Vos 90 premiers jours ? »).
   Pour chacune, une trame STAR tirée d'une expérience précise du CV (cite le poste et l'employeur) :
   situation en 1-2 phrases, tâche en 1, action en 2-3, résultat. star = null si rien ne convient.
4. points_faibles : pour chaque manque majeur ou critique de l'analyse, la question piège probable
   et une réponse honnête qui s'appuie sur une compétence voisine réelle, sans s'excuser.
5. questions_a_poser : questions ouvertes au recruteur (réussite à 30/60/90 jours, défis de l'équipe,
   mesure de la performance, organisation). Rien qui soit déjà dans l'offre, rien sur le salaire.
6. salaire : stratégie seulement. Faire annoncer d'abord la fourchette prévue ; citer celle de l'offre
   si elle existe ; sinon, le candidat fixe la sienne avant l'entretien (ne propose aucun montant).
   Arguments de valeur tirés du CV, éléments négociables hors fixe (télétravail, formation, date
   de début, intitulé, prime). Ne jamais révéler le salaire actuel ni citer une offre concurrente.
7. a_eviter : critiques d'anciens employeurs, sujets sensibles, erreurs propres à ce poste.

Phrases courtes. Français, ou anglais si l'offre est en anglais."""

SYSTEME_RELANCE = """Tu rédiges une relance courte (60 à 110 mots) pour une candidature restée sans réponse.
Zéro invention : uniquement des faits du CV et de l'offre.
Structure : rappel en une phrase (poste, date d'envoi) ; un élément NOUVEAU et précis — un autre besoin
de l'offre relié à une expérience réelle du CV, ou le lien du portfolio — sans répéter le premier message ;
une proposition simple et sans pression (un court échange).
Interdits : s'excuser, culpabiliser (« sans nouvelles de votre part »), « Dans l'attente »,
« J'aimerais avoir l'opportunité ».
Objet : « Re : » + l'objet du premier message s'il est fourni.
Signature : nom, téléphone, portfolio. Langue de l'offre."""


def _offre_bloc(offre: Offre, note: Note) -> str:
    return f"""<offre>
Titre : {note.intitule or offre.titre}
Entreprise : {note.entreprise or offre.entreprise or "non précisée"}
Lieu : {offre.lieu}

{offre.description[:15000]}
</offre>

<analyse>
Score : {note.score}/100 — {note.verdict}
Points forts : {"; ".join(note.points_forts)}
Manques : {"; ".join(f"{m.intitule} ({m.gravite})" for m in note.manques) or "; ".join(note.ecarts)}
Salaire indiqué dans l'offre : {note.salaire or "aucun"}
</analyse>"""


def preparer_entretien(llm: LLM, offre: Offre, note: Note) -> PreparationEntretien:
    consigne = "Prépare l'entretien pour cette offre.\n\n" + _offre_bloc(offre, note)
    return llm.demander(config()["modeles"]["redaction"], SYSTEME_ENTRETIEN, cv_texte(note.langue),
                        consigne, PreparationEntretien, max_tokens=10000)


def rediger_relance(llm: LLM, offre: Offre, note: Note, envoye_le: str, premier_message: str = "") -> Relance:
    consigne = (f"Candidature envoyée le {envoye_le or '?'}.\n\n"
                f"<premier_message>\n{premier_message or '(non conservé)'}\n</premier_message>\n\n"
                + _offre_bloc(offre, note))
    return llm.demander(config()["modeles"]["redaction"], SYSTEME_RELANCE, cv_texte(note.langue),
                        consigne, Relance, max_tokens=1500)


def entretien_markdown(offre: Offre, note: Note, p: PreparationEntretien) -> str:
    l = [f"# Entretien — {note.intitule or offre.titre}", f"**{note.entreprise or offre.entreprise or ''}**", "",
         "## Compétences évaluées", *[f"- {c}" for c in p.competences_evaluees], "",
         "## Présentez-vous", p.pitch, "", "## Questions probables"]
    for q in p.questions:
        l += ["", f"### {q.question}", f"*{q.categorie} · probabilité {q.probabilite}*"]
        if q.conseil:
            l.append(f"> {q.conseil}")
        if q.star:
            s = q.star
            l += [f"- **Situation** : {s.situation}", f"- **Tâche** : {s.tache}", f"- **Action** : {s.action}",
                  f"- **Résultat** : {s.resultat}", f"- *Source : {s.experience_source}*"]
        else:
            l.append("- Aucune expérience du CV ne convient : prépare une réponse honnête.")
    l += ["", "## Points faibles"]
    for f in p.points_faibles:
        l += [f"- **{f.manque}** — « {f.question_piege} »", f"  {f.reponse}"]
    l += ["", "## Questions à poser", *[f"- {q}" for q in p.questions_a_poser],
          "", "## Salaire", f"Fourchette de l'offre : {p.salaire.fourchette_offre or 'non indiquée'}", "",
          p.salaire.strategie, "", "**Arguments**", *[f"- {a}" for a in p.salaire.arguments],
          "", "**Négociable**", *[f"- {a}" for a in p.salaire.negociable],
          "", "**Phrases**", *[f"- « {a} »" for a in p.salaire.phrases],
          "", "## À éviter", *[f"- {a}" for a in p.a_eviter]]
    if p.a_verifier:
        l += ["", "## À vérifier avant l'entretien", *[f"- {a}" for a in p.a_verifier]]
    return "\n".join(l) + "\n"
