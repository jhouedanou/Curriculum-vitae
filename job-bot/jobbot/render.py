"""Mise en page : CV et lettre en HTML (+ PDF), message et fiche de l'offre."""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import RACINE, SORTIE, config, cv
from .models import Dossier, Note, Offre
from .sources.base import normaliser

TEXTES = {
    "fr": dict(profil="Profil", competences="Compétences clés", experience="Expérience professionnelle", anterieures="Expériences antérieures",
               projets="Projets sélectionnés", formation="Formation", langues="Langues",
               infos="Informations", lettre="Lettre de motivation", objet="Objet",
               appel="Madame, Monsieur,",
               formule="Dans l'attente de votre retour, je vous prie d'agréer, Madame, Monsieur, "
                       "l'expression de mes salutations distinguées.",
               ne="Né le", permis="Permis"),
    "en": dict(profil="Profile", competences="Key skills", experience="Professional experience", anterieures="Earlier roles",
               projets="Selected projects", formation="Education", langues="Languages",
               infos="Details", lettre="Cover letter", objet="Subject",
               appel="Dear Hiring Manager,", formule="Sincerely,",
               ne="Born", permis="Driving licence"),
}
MOIS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
           "septembre", "octobre", "novembre", "décembre"]

env = Environment(loader=FileSystemLoader(RACINE / "templates"), autoescape=select_autoescape(["html"]))


def _date_lettre(langue: str, ville: str) -> str:
    d = date.today()
    ville = ville.split(",")[0]
    if langue == "en":
        return f"{ville}, {d.strftime('%B')} {d.day}, {d.year}"
    return f"{ville}, le {d.day} {MOIS_FR[d.month - 1]} {d.year}"


def _slug(texte: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", normaliser(texte)).strip("-")[:50] or "offre"


def generer(offre: Offre, note: Note, dossier: Dossier) -> Path:
    langue = note.langue
    data = cv(langue)
    ident = data["identite"]
    t = TEXTES[langue]
    css = (RACINE / "templates" / "style.css").read_text(encoding="utf-8")

    dossier_sortie = SORTIE / f"{date.today():%Y-%m-%d}_{offre.id}_{_slug(note.entreprise or offre.titre)}"
    dossier_sortie.mkdir(parents=True, exist_ok=True)
    nom_fichier = _slug(ident["nom"]).title().replace("-", "_")

    # ── CV ────────────────────────────────────────────
    exp_cv = {e["id"]: e for e in data["experiences"]}
    experiences = [{**exp_cv[e.id], "puces": e.puces} for e in dossier.cv.experiences if e.id in exp_cv]
    proj_cv = {p["id"]: p for p in data["projets"]}
    projets = [proj_cv[i] for i in dossier.cv.projets if i in proj_cv]
    perso = []
    ip = data.get("infos_perso", {})
    if ip.get("afficher"):
        if ip.get("date_naissance"):
            perso.append(f"{t['ne']} {ip['date_naissance']}")
        if ip.get("situation"):
            perso.append(ip["situation"])
        if ip.get("permis"):
            perso.append(f"{t['permis']} {ip['permis']}")
    photo = ident.get("photo") or ""
    photo_uri = (RACINE / photo).resolve().as_uri() if photo and (RACINE / photo).exists() else ""

    html_cv = env.get_template("cv.html").render(
        langue=langue, t=t, css=css, id=ident, a=dossier.cv, photo=photo_uri,
        experiences=experiences, anterieures=data.get("experiences_anterieures", []),
        projets=projets, formation=data.get("formation", []), langues=data.get("langues", []),
        perso=perso,
    )
    _ecrire(dossier_sortie / f"CV_{nom_fichier}", html_cv)

    # ── Lettre ────────────────────────────────────────
    if dossier.lettre:
        html_lettre = env.get_template("lettre.html").render(
            langue=langue, t=t, css=css, id=ident, l=dossier.lettre,
            date=_date_lettre(langue, ident.get("ville", "Abidjan")),
        )
        _ecrire(dossier_sortie / f"Lettre_{nom_fichier}", html_lettre)

    # ── Message ───────────────────────────────────────
    a_qui = note.email_candidature or "(adresse non trouvée : voir l'offre)"
    (dossier_sortie / "message.txt").write_text(
        f"À : {a_qui}\nObjet : {dossier.message.objet_email}\n\n{dossier.message.texte}\n",
        encoding="utf-8",
    )

    # ── Fiche de l'offre (pour relire avant d'envoyer) ─
    (dossier_sortie / "offre.md").write_text(_fiche(offre, note, dossier), encoding="utf-8")
    # Pour l'interface web : le dossier tel que rédigé et vérifié
    (dossier_sortie / "dossier.json").write_text(dossier.model_dump_json(indent=2), encoding="utf-8")
    return dossier_sortie


def _ecrire(base: Path, html: str) -> None:
    base.with_suffix(".html").write_text(html, encoding="utf-8")
    if not config().get("pdf", True):
        return
    try:
        from weasyprint import HTML
    except Exception:
        print("  (WeasyPrint absent : HTML seulement — ouvre-le et fais Imprimer > PDF)")
        return
    HTML(string=html, base_url=str(RACINE)).write_pdf(base.with_suffix(".pdf"))


def _fiche(offre: Offre, note: Note, d: Dossier) -> str:
    lignes = [
        f"# {note.intitule or offre.titre}",
        f"**Entreprise :** {note.entreprise or offre.entreprise or '?'}  ",
        f"**Lieu :** {offre.lieu}  ",
        f"**Lien :** {offre.url}  ",
        f"**Source :** {offre.source}  ",
        f"**Date limite :** {note.date_limite or '?'}  ",
        f"**Envoyer à :** {note.email_candidature or '?'}  ",
        "",
        f"## Score : {note.score}/100",
        note.verdict,
        "",
        "**Points forts**",
        *[f"- {p}" for p in note.points_forts],
        "",
        "**Écarts**",
        *[f"- {p}" for p in note.ecarts],
    ]
    if note.consignes:
        lignes += ["", "## Consignes de candidature", note.consignes]
    if note.alerte:
        lignes += ["", f"## ⚠️ Alerte : {note.alerte}"]
    if d.avertissements:
        lignes += ["", "## À vérifier avant d'envoyer", *[f"- {a}" for a in d.avertissements]]
    lignes += ["", "---", "## Texte de l'offre", "", offre.description]
    return "\n".join(lignes) + "\n"
