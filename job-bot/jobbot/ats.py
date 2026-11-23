"""Sorties lisibles par les logiciels de tri des recruteurs (ATS) : Markdown et HTML simple.

Règles suivies : une seule colonne, titres de sections standards, pas de tableau, pas d'image,
pas d'icône, coordonnées dans le corps du texte, dates en clair, puces simples.
Le contenu est le même que celui du CV mis en page : rien n'est ajouté ici.
"""
from __future__ import annotations

from typing import Optional

TITRES = {
    "fr": dict(profil="Profil professionnel", competences="Compétences", experience="Expérience professionnelle",
               anterieures="Autres expériences", projets="Projets", formation="Formation", langues="Langues",
               email="Email", telephone="Téléphone", portfolio="Portfolio", github="GitHub", objet="Objet",
               a="À", appel="Madame, Monsieur,",
               formule="Dans l'attente de votre retour, je vous prie d'agréer, Madame, Monsieur, "
                       "l'expression de mes salutations distinguées."),
    "en": dict(profil="Professional Summary", competences="Skills", experience="Work Experience",
               anterieures="Earlier Roles", projets="Projects", formation="Education", langues="Languages",
               email="Email", telephone="Phone", portfolio="Portfolio", github="GitHub", objet="Subject",
               a="To", appel="Dear Hiring Manager,", formule="Sincerely,"),
}


def _emails(ident: dict) -> str:
    return " | ".join(e for e in (ident.get("email"), ident.get("email2")) if e)


def coordonnees(ident: dict, langue: str) -> list[str]:
    """Lignes « Libellé : valeur », sans icône : c'est ce qu'un ATS sait lire."""
    t = TITRES[langue]
    lignes = [ident.get("ville", "")]
    if _emails(ident):
        lignes.append(f"{t['email']} : {_emails(ident)}")
    if ident.get("telephone"):
        lignes.append(f"{t['telephone']} : {ident['telephone']}")
    if ident.get("portfolio"):
        lignes.append(f"{t['portfolio']} : {ident['portfolio']}")
    if ident.get("github"):
        lignes.append(f"{t['github']} : {ident['github']}")
    return [l for l in lignes if l]


def cv_markdown(langue: str, ident: dict, titre: str, resume: str, competences: list[str],
                experiences: list[dict], anterieures: list[str], projets: list[dict],
                formation: list[dict], langues: list[dict]) -> str:
    t = TITRES[langue]
    md = [f"# {ident['nom']}", "", f"**{titre}**", ""]
    md += [l + "  " for l in coordonnees(ident, langue)]
    md += ["", f"## {t['profil']}", "", resume, "", f"## {t['competences']}", "", ", ".join(competences), "",
           f"## {t['experience']}", ""]
    for e in experiences:
        md += [f"### {e['poste']}", f"**{e['entreprise']}** — {e['lieu']}  ", e["periode"], ""]
        md += [f"- {p}" for p in e["puces"]]
        md.append("")
    if anterieures:
        md += [f"### {t['anterieures']}", ""] + [f"- {x}" for x in anterieures] + [""]
    if projets:
        md += [f"## {t['projets']}", ""]
        for p in projets:
            md += [f"### {p['nom']}", f"{p['role']} — {', '.join(p.get('technos', []))}  ", f"{p['description']}  ",
                   p["url"], ""]
    md += [f"## {t['formation']}", ""]
    for f in formation:
        md += [f"### {f['diplome']}", f"{f['ecole']} — {f['annees']}", ""]
    md += [f"## {t['langues']}", ""] + [f"- {l['langue']} : {l['niveau']}" for l in langues]
    return "\n".join(md).rstrip() + "\n"


def lettre_markdown(langue: str, ident: dict, objet: str, destinataire: str, paragraphes: list[str],
                    date: str) -> str:
    t = TITRES[langue]
    md = [f"# {ident['nom']}", ""]
    md += [l + "  " for l in coordonnees(ident, langue)]
    md += ["", date, "", f"**{destinataire}**", "", f"## {t['objet']} : {objet}", "", t["appel"], ""]
    for p in paragraphes:
        md += [p, ""]
    md += [t["formule"], "", f"**{ident['nom']}**"]
    return "\n".join(md) + "\n"


def email_markdown(langue: str, a_qui: Optional[str], objet: str, texte: str) -> str:
    t = TITRES[langue]
    return "\n".join([f"**{t['a']} :** {a_qui or '(adresse non trouvée : voir l’offre)'}  ",
                      f"**{t['objet']} :** {objet}", "", "---", "", texte.strip(), ""])
