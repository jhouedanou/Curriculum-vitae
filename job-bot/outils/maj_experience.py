"""Met à jour les années par compétence dans les CV Markdown déjà fabriqués, puis leurs PDF.

Les nombres viennent de jobbot/experience.py, donc des dates de cv.yaml.
  python job-bot/outils/maj_experience.py            réécrit les fichiers qui ne sont plus à jour
  python job-bot/outils/maj_experience.py --pdf      … et refait leurs PDF
  python job-bot/outils/maj_experience.py --verifier sort en erreur si un fichier n'est pas à jour
"""
from __future__ import annotations

import argparse
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
    """Contenu attendu de chaque fichier : les années par compétence des CV Markdown.
    Le total n'est écrit nulle part (« plusieurs années »)."""
    sortie = {}
    for langue, yml, md in (("fr", "cv.yaml", "cv_HOUEDANOU.md"), ("en", "cv_en.yaml", "cv_HOUEDANOUen.md")):
        d = experience.completer(_cv(yml), aujourdhui)
        comp = [c["annees"] for cat in d["competences"] for c in cat["items"]]
        motif = r"\((?P<n>\d+) ans d'expérience," if langue == "fr" else r"\((?P<n>\d+) years experience,"
        sortie[md] = _remplacer((DEPOT / md).read_text(encoding="utf-8"), motif, comp, md)
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
    print(len(changes), "fichier(s) modifié(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
