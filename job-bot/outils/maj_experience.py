"""Met à jour les années d'expérience dans les fichiers déjà fabriqués (CV Markdown, CV HTML, portfolio).

Les nombres viennent de jobbot/experience.py, donc des dates de cv.yaml.
  python job-bot/outils/maj_experience.py            réécrit les fichiers qui ne sont plus à jour
  python job-bot/outils/maj_experience.py --pdf      … et refait leurs PDF
  python job-bot/outils/maj_experience.py --verifier sort en erreur si un fichier n'est pas à jour
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

DEPOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(DEPOT / "job-bot"))

import yaml  # noqa: E402

from jobbot import experience  # noqa: E402


def _cv(nom: str) -> dict:
    return yaml.safe_load((DEPOT / "job-bot" / nom).read_text(encoding="utf-8"))


def _remplacer(texte: str, motif: str, valeurs: list, nom: str) -> str:
    """Remplace dans l'ordre chaque nombre capturé par `motif` (groupe « n »)."""
    trouves = list(re.finditer(motif, texte))
    if len(trouves) != len(valeurs):
        raise SystemExit(f"{nom} : {len(trouves)} occurrences de {motif!r}, {len(valeurs)} attendues")
    for m, v in reversed(list(zip(trouves, valeurs))):
        texte = texte[:m.start("n")] + str(v) + texte[m.end("n"):]
    return texte


def fichiers(aujourdhui: date | None = None) -> dict[str, str]:
    """Contenu attendu de chaque fichier, à partir des fichiers actuels."""
    sortie = {}
    for langue, yml in (("fr", "cv.yaml"), ("en", "cv_en.yaml")):
        d = experience.completer(_cv(yml), aujourdhui)
        n = d["annees_experience"]
        comp = [c["annees"] for cat in d["competences"] for c in cat["items"]]
        md = "cv_HOUEDANOU.md" if langue == "fr" else "cv_HOUEDANOUen.md"
        html = f"CV_Jean_Luc_Houedanou_{langue.upper()}.html"
        s = (DEPOT / md).read_text(encoding="utf-8")
        if langue == "fr":
            s = _remplacer(s, r"\((?P<n>\d+) ans d'expérience,", comp, md)
            s = _remplacer(s, r"plus de (?P<n>\d+) ans d'expertise", [n], md)
        else:
            s = _remplacer(s, r"\((?P<n>\d+) years experience,", comp, md)
            s = _remplacer(s, r"over (?P<n>\d+) years of expertise", [n], md)
        sortie[md] = s
        s = (DEPOT / html).read_text(encoding="utf-8")
        motif = r"plus de (?P<n>\d+) ans d&#39;expertise" if langue == "fr" else r"over (?P<n>\d+) years of experience"
        sortie[html] = _remplacer(s, motif, [n], html)
        doc = f"CV Jean Luc Houedanou {langue.upper()}.doc"   # version Word (pas de PDF tiré de ce fichier)
        s = (DEPOT / doc).read_text(encoding="utf-8")
        motif = r"plus de <b>(?P<n>\d+) ans d'expérience</b>" if langue == "fr" else r"over <b>(?P<n>\d+) years of experience</b>"
        s = _remplacer(s, motif, [n], doc)
        sortie[doc] = _remplacer(s, r'color:#1f5a73;">(?P<n>\d+)\+</span><br><span[^>]*>(?:ans|years) ', [n], doc)
    # Portfolio : les périodes ; le navigateur fait le calcul à chaque visite.
    per = [{"debut": a, "fin": b} for a, b in experience.periodes(_cv("cv.yaml"))]
    sortie["experience-data.js"] = (
        "// Généré par job-bot/outils/maj_experience.py à partir de job-bot/cv.yaml. Ne pas modifier à la main.\n"
        "// Années d'expérience = mois travaillés (un mois sur deux postes compte une fois), arrondi à l'année inférieure.\n"
        f"window.PERIODES_EXPERIENCE = {json.dumps(per)};\n"
        "window.anneesExperience = function (aujourdhui) {\n"
        "    var d = aujourdhui || new Date(), fin = d.getFullYear() * 12 + d.getMonth(), mois = {};\n"
        "    var m = function (t) { var p = t.split('-'); return +p[0] * 12 + (+p[1] - 1); };\n"
        "    window.PERIODES_EXPERIENCE.forEach(function (p) {\n"
        "        for (var i = m(p.debut); i <= (p.fin ? m(p.fin) : fin); i++) mois[i] = 1;\n"
        "    });\n"
        "    return Math.floor(Object.keys(mois).length / 12);\n"
        "};\n"
        "window.ANNEES_EXPERIENCE = window.anneesExperience();\n")
    return sortie


PDF_MD = ["cv_HOUEDANOU.md", "cv_HOUEDANOUen.md"]
# page HTML → PDF (impression Chromium)
PDF_HTML = {
    "CV_Jean_Luc_Houedanou_FR.html": "CV_Jean_Luc_Houedanou_FR.pdf",
    "CV_Jean_Luc_Houedanou_EN.html": "CV_Jean_Luc_Houedanou_EN.pdf",
}


def faire_pdf(noms: list[str]) -> None:
    md = [n for n in noms if n in PDF_MD]
    if md:
        subprocess.run(["npx", "-y", "md-to-pdf", *md, "--stylesheet", "github-markdown.css",
                        "--body-class=markdown-body", "--launch-options", '{"args":["--no-sandbox"]}',
                        "--pdf-options", '{"margin":"5mm"}'], cwd=DEPOT, check=True, stdin=subprocess.DEVNULL)
    paires = [x for n in noms if n in PDF_HTML for x in (n, PDF_HTML[n])]
    if paires:
        subprocess.run(["node", str(Path(__file__).with_name("imprimer.js")), *paires], cwd=DEPOT, check=True)
    for n in md:
        print("PDF", n[:-3] + ".pdf")
    for n in paires[1::2]:
        print("PDF", n)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--pdf", action="store_true")
    a = p.parse_args()
    changes = [n for n, s in fichiers().items()
               if not (DEPOT / n).exists() or (DEPOT / n).read_text(encoding="utf-8") != s]
    if a.verifier:
        for n in changes:
            print("pas à jour :", n)
        return 1 if changes else 0
    for n in changes:
        (DEPOT / n).write_text(fichiers()[n], encoding="utf-8")
        print("mis à jour :", n)
    if a.pdf and changes:
        faire_pdf(changes)
    print(f"{experience.annees_experience(_cv('cv.yaml'))} ans d'expérience ;", len(changes), "fichier(s) modifié(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
