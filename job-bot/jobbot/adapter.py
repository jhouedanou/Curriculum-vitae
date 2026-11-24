"""Adapter le CV et la lettre à une offre, sans IA : brouillons en Markdown, puis mise en page.

Le brouillon ne rédige rien : il choisit et réordonne ce qui est dans cv.yaml d'après les mots de l'offre.
- Compétences du CV citées par l'offre : placées en tête.
- Réalisations et projets qui contiennent ces mots : placés en tête.
- Mots-clés de l'offre absents du CV : listés, jamais ajoutés.
L'utilisateur relit et modifie le Markdown dans l'interface ; le bot en tire le HTML et le PDF.
"""
from __future__ import annotations

import html
import re
from datetime import date
from pathlib import Path
from typing import Optional

from . import ats, render
from .config import cv
from .models import Offre
from .sources.base import normaliser

# Mots fréquents dans les offres web / design / gestion de projet. Sert seulement à signaler
# ce que l'offre demande et que le CV ne cite pas.
VOCABULAIRE = [
    "React", "React Native", "Next.js", "Angular", "Svelte", "TypeScript", "Node.js", "Express", "NestJS",
    "Python", "Django", "Flask", "Java", "Spring", "Kotlin", "Swift", "Flutter", "Dart", "C#", ".NET", "Go",
    "Ruby", "Symfony", "WordPress", "Drupal", "Shopify", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
    "GraphQL", "REST", "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform", "Ansible", "Jenkins",
    "GitHub Actions", "GitLab", "Git", "CI/CD", "Tailwind", "Sass", "Bootstrap", "Webpack", "Vite",
    "Figma", "Adobe XD", "Sketch", "Photoshop", "Illustrator", "InDesign", "After Effects", "Canva",
    "Design system", "Wireframes", "Prototypes", "Material Design", "Human Interface Guidelines",
    "Tests utilisateurs", "UX Research", "Accessibilité", "WCAG", "SEO", "Google Analytics", "Matomo",
    "Scrum", "Kanban", "Agile", "Jira", "Trello", "Notion", "Product Owner", "PMP", "Prince2",
    "Tests unitaires", "Jest", "Cypress", "Playwright", "PHPUnit", "Microservices", "API", "OAuth",
    "Power BI", "Excel", "SQL", "Linux", "Anglais", "English",
]
MOTS_EN = {"the", "and", "you", "with", "our", "will", "for", "are", "your", "team", "experience", "we"}
MOTS_FR = {"le", "la", "les", "des", "vous", "nous", "avec", "pour", "une", "est", "votre", "notre", "du"}

TXT = {
    "fr": dict(objet="Candidature au poste de {titre}", dest="Service Recrutement{ent}",
               p1="Je vous présente ma candidature au poste de {titre}{chez}.",
               p3_avec="Votre annonce demande {liste}. Ces compétences figurent dans mon CV : {details}.",
               p3_sans="[À compléter : relie deux exigences de l'annonce à des faits de ton CV.]",
               p4="Quelques réalisations en ligne : {projets}.",
               p5="Mon portfolio complet est en ligne : {portfolio}. Je suis à votre disposition pour un entretien.",
               ans="{n} ans", email_objet="Candidature — {titre} — {nom}", bonjour="Bonjour,",
               email_p1="Je vous envoie ma candidature au poste de {titre}{chez}.",
               email_p2="Mon CV{lettre} sont joints à ce message.", et_lettre=" et ma lettre de motivation",
               email_p2_seul="Mon CV est joint à ce message.",
               email_p3="Portfolio : {portfolio}", chez=" chez {ent}", et=" et "),
    "en": dict(objet="Application for the {titre} position", dest="Hiring Team{ent}",
               p1="I am applying for the {titre} position{chez}.",
               p3_avec="Your posting asks for {liste}. These skills are on my CV: {details}.",
               p3_sans="[To complete: link two requirements of the posting to facts from your CV.]",
               p4="A few projects online: {projets}.",
               p5="My full portfolio is online: {portfolio}. I am available for an interview.",
               ans="{n} years", email_objet="Application — {titre} — {nom}", bonjour="Hello,",
               email_p1="Please find my application for the {titre} position{chez}.",
               email_p2="My CV{lettre} are attached.", et_lettre=" and cover letter",
               email_p2_seul="My CV is attached.",
               email_p3="Portfolio: {portfolio}", chez=" at {ent}", et=" and "),
}


# ── Lecture de l'offre ───────────────────────────────────────
def langue_offre(texte: str) -> str:
    mots = re.findall(r"[a-zà-ÿ']+", texte.lower())
    en = sum(m in MOTS_EN for m in mots)
    fr = sum(m in MOTS_FR for m in mots)
    return "en" if en > fr else "fr"


def _cite(texte_norm: str, mot: str) -> bool:
    m = re.escape(normaliser(mot))
    return bool(re.search(rf"(?<![a-z0-9]){m}(?![a-z0-9])", texte_norm))


def mots_cles(offre_texte: str, langue: str = "fr") -> dict:
    """Compétences du CV citées par l'offre, et mots courants de l'offre absents du CV."""
    data = cv(langue)
    t = normaliser(offre_texte)
    competences = [c["nom"] for cat in data["competences"] for c in cat["items"]]
    technos = [x for p in data["projets"] for x in p.get("technos", [])]
    connus = {normaliser(x) for x in competences + technos}
    presents = [c for c in competences if _cite(t, c)]
    technos_citees = sorted({x for x in technos if _cite(t, x) and x not in presents})
    absents = [v for v in VOCABULAIRE
               if _cite(t, v) and not any(normaliser(v) in k or k in normaliser(v) for k in connus)]
    return {"presents": presents, "technos": technos_citees, "absents": absents}


def titre_poste(offre: Offre) -> str:
    """« DESIGNER UX UI (H/F) | Entreprise » → « Designer UX UI (H/F) »."""
    t = re.split(r"\s+[|•]\s+|\s+—\s+|\s+-\s+(?=[A-Z])", offre.titre.strip())[0].strip(" :-") or offre.titre.strip()
    if t.isupper() and len(t) > 6:
        t = t.capitalize()
        t = re.sub(r"\b(ux|ui|h/f|f/h|it|rh|seo|cto|php|api)\b", lambda m: m.group(0).upper(), t, flags=re.I)
    return t


def surligner(offre_texte: str, mots: list[str]) -> str:
    """Texte de l'offre en HTML sûr, avec les mots trouvés entourés de <mark>."""
    sur = html.escape(offre_texte)
    for mot in sorted(set(mots), key=len, reverse=True):
        motif = re.compile(rf"(?<![\w>])({re.escape(html.escape(mot))})(?![\w<])", re.I)
        sur = motif.sub(r"<mark>\1</mark>", sur)
    return sur


# ── Brouillons ───────────────────────────────────────────────
def _poids(texte: str, cles: list[str]) -> int:
    n = normaliser(texte)
    return sum(_cite(n, c) for c in cles)


def brouillons(offre: Offre) -> dict:
    """CV, lettre et email en Markdown, tirés de cv.yaml et réordonnés d'après l'offre."""
    langue = langue_offre(offre.description)
    data, x = cv(langue), TXT[langue]
    ident = data["identite"]
    mc = mots_cles(offre.description, langue)
    cles = mc["presents"] + mc["technos"]
    titre = titre_poste(offre)

    tous = [c["nom"] for cat in data["competences"] for c in cat["items"]]
    competences = (mc["presents"] + [c for c in tous if c not in mc["presents"]])[:14]

    experiences = []
    for e in data["experiences"]:
        puces = sorted(e["realisations"], key=lambda p: -_poids(p, cles))  # tri stable : ordre du CV à égalité
        experiences.append({**e, "puces": puces[:4 if e is data["experiences"][0] else 3]})

    classes = sorted(data["projets"], key=lambda p: -_poids(" ".join([p["nom"], p["description"], *p.get("technos", [])]), cles))
    projets = classes[:5]

    cv_md = ats.cv_markdown(langue, ident, titre, " ".join(data["resume"].split()), competences, experiences,
                            data.get("experiences_anterieures", []), projets, data.get("formation", []),
                            data.get("langues", []))

    ent = offre.entreprise.strip()
    chez = x["chez"].format(ent=ent) if ent else ""
    annees = {c["nom"]: c.get("annees") for cat in data["competences"] for c in cat["items"]}
    top = mc["presents"][:4]
    if top:
        liste = ", ".join(top[:-1]) + (x["et"] + top[-1] if len(top) > 1 else top[0])
        details = ", ".join(f"{c} ({x['ans'].format(n=annees[c])})" if annees.get(c) else c for c in top)
        p3 = x["p3_avec"].format(liste=liste, details=details)
    else:
        p3 = x["p3_sans"]
    paragraphes = [
        x["p1"].format(titre=titre, chez=chez),
        " ".join(data["resume"].split()),
        p3,
        x["p4"].format(projets=", ".join(f"{p['nom']} ({p['url']})" for p in projets[:3])),
        x["p5"].format(portfolio=ident.get("portfolio", "")),
    ]
    lettre_md = ats.lettre_markdown(langue, ident, x["objet"].format(titre=titre),
                                    x["dest"].format(ent=f" — {ent}" if ent else ""), paragraphes,
                                    render._date_lettre(langue, ident.get("ville", "Abidjan")))

    corps = "\n\n".join([x["bonjour"], x["email_p1"].format(titre=titre, chez=chez),
                         x["email_p2"].format(lettre=x["et_lettre"]), x["email_p3"].format(portfolio=ident.get("portfolio", "")),
                         "\n".join([ident["nom"], ident.get("telephone", "")])])
    email_md = ats.email_markdown(langue, None, x["email_objet"].format(titre=titre, nom=ident["nom"]), corps)
    return {"langue": langue, "titre": titre, "cv": cv_md, "lettre": lettre_md, "email": email_md, "mots": mc}


# ── Enregistrement : Markdown → HTML et PDF ──────────────────
CSS_ATS = """@page { size: A4; margin: 14mm 16mm 13mm 16mm; }
* { box-sizing: border-box; }
body { margin: 0; background: #fff; color: #000; font-family: Arial, Helvetica, sans-serif; font-size: 10pt; line-height: 1.33; }
h1 { margin: 0 0 4pt; font-size: 18pt; }
h2 { margin: 10pt 0 4pt; padding-bottom: 2pt; border-bottom: 1px solid #000; font-size: 11.5pt; text-transform: uppercase; }
h3 { margin: 6pt 0 0; font-size: 10pt; }
p { margin: 0 0 3pt; }
ul { margin: 3pt 0 0; padding-left: 16pt; }
li { margin-bottom: 1pt; }
a { color: #000; text-decoration: none; }
hr { border: 0; border-top: 1px solid #000; margin: 8pt 0; }
h3, h3 + p { break-after: avoid; }
body.lettre { font-size: 11pt; line-height: 1.5; }
body.lettre h2 { border: 0; text-transform: none; font-size: 11pt; margin: 14pt 0 10pt; }
body.lettre p { margin: 0 0 9pt; }
@media screen { body { max-width: 210mm; margin: 24px auto; padding: 0 16px; } }"""


def markdown_vers_html(md: str, titre: str, classe: str = "") -> str:
    """Page HTML simple (une colonne, sans image) à partir du Markdown saisi."""
    import markdown

    md = re.sub(r"<[^>]+>", "", md)  # pas de HTML brut : le document reste lisible par un ATS
    corps = markdown.markdown(md, extensions=["sane_lists"], output_format="html")
    return (f'<!doctype html>\n<html lang="fr">\n<head>\n<meta charset="utf-8">\n<title>{html.escape(titre)}</title>\n'
            f"<style>\n{CSS_ATS}\n</style>\n</head>\n<body class=\"{classe}\">\n{corps}\n</body>\n</html>\n")


def _email_vers_message(email_md: str) -> str:
    """Email en Markdown → message.txt (« À : / Objet : / corps »), lu par la page de l'offre."""
    tete, _, corps = email_md.partition("\n---\n")
    champs = dict(re.findall(r"\*\*(À|To|Objet|Subject) :\*\*\s*(.*)", tete))
    a = (champs.get("À") or champs.get("To") or "").strip()
    objet = (champs.get("Objet") or champs.get("Subject") or "").strip()
    return f"À : {a}\nObjet : {objet}\n\n{corps.strip()}\n"


def dossier_de(offre: Offre, existant: Optional[Path] = None) -> Path:
    if existant and existant.exists():
        return existant
    return render.SORTIE / f"{date.today():%Y-%m-%d}_{offre.id}_{render._slug(offre.entreprise or titre_poste(offre))}"


def lire(chemin: Optional[Path], nom: str) -> Optional[str]:
    """Le Markdown déjà enregistré pour ce dossier, s'il existe."""
    if chemin and (chemin / nom).exists():
        return (chemin / nom).read_text(encoding="utf-8")
    return None


def enregistrer(offre: Offre, cv_md: str, lettre_md: str, email_md: str, existant: Optional[Path] = None) -> Path:
    """Écrit les trois Markdown, puis le HTML et le PDF du CV et de la lettre. Une lettre vide est retirée."""
    chemin = dossier_de(offre, existant)
    chemin.mkdir(parents=True, exist_ok=True)
    nom = render._slug(cv()["identite"]["nom"]).title().replace("-", "_")

    (chemin / f"CV_ATS_{nom}.md").write_text(cv_md.strip() + "\n", encoding="utf-8")
    render._ecrire(chemin / f"CV_ATS_{nom}", markdown_vers_html(cv_md, "CV"))

    if lettre_md.strip():
        (chemin / f"Lettre_{nom}.md").write_text(lettre_md.strip() + "\n", encoding="utf-8")
        render._ecrire(chemin / f"Lettre_{nom}", markdown_vers_html(lettre_md, "Lettre de motivation", "lettre"))
    else:
        for ext in (".md", ".html", ".pdf"):
            (chemin / f"Lettre_{nom}{ext}").unlink(missing_ok=True)

    (chemin / f"Email_{nom}.md").write_text(email_md.strip() + "\n", encoding="utf-8")
    (chemin / "message.txt").write_text(_email_vers_message(email_md), encoding="utf-8")
    if not (chemin / "offre.md").exists():
        (chemin / "offre.md").write_text(f"# {offre.titre}\n\n**Lien :** {offre.url}\n\n---\n\n{offre.description}\n",
                                         encoding="utf-8")
    return chemin
