"""JobBot — trouve les offres qui collent à ton CV et prépare tes candidatures.

Commandes :
  python -m jobbot go                    tout faire : collecter, noter, préparer les meilleurs dossiers
  python -m jobbot collecter             récupérer les nouvelles offres
  python -m jobbot noter                 noter les offres pas encore notées (IA)
  python -m jobbot top [--min 60]        voir le classement
  python -m jobbot preparer 12           préparer le dossier de l'offre n°12
  python -m jobbot preparer 12 --lettre  … en forçant une lettre de motivation
  python -m jobbot coller offre.txt      offre copiée à la main (LinkedIn, email…) ; « - » = coller dans le terminal
  python -m jobbot statut 12 envoye      suivre une offre : a_relire, envoye, entretien, refus, ignore, nouveau
  python -m jobbot relances              candidatures envoyées à relancer
  python -m jobbot relancer 12           rédiger le message de relance (IA)
  python -m jobbot entretien 12          préparer l'entretien : questions, réponses STAR, questions à poser (IA)
  python -m jobbot web                   ouvrir l'interface (ordinateur + téléphone sur le même Wi-Fi)
"""
from __future__ import annotations

import argparse
import sys

from . import pipeline
from .config import config
from .db import STATUTS, Base, detail_note
from .llm import Claude, charger_env


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="jobbot", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("go")
    sub.add_parser("collecter")
    sub.add_parser("noter")
    t = sub.add_parser("top")
    t.add_argument("--min", type=int, default=None, help="score minimum (défaut : seuil de config.yaml)")
    pr = sub.add_parser("preparer")
    pr.add_argument("id", type=int)
    g = pr.add_mutually_exclusive_group()
    g.add_argument("--lettre", dest="lettre", action="store_true", default=None)
    g.add_argument("--sans-lettre", dest="lettre", action="store_false")
    c = sub.add_parser("coller")
    c.add_argument("fichier", help="fichier texte de l'offre, ou - pour coller dans le terminal")
    c.add_argument("--url", default="")
    c.add_argument("--lettre", action="store_true", default=None)
    s = sub.add_parser("statut")
    s.add_argument("id", type=int)
    s.add_argument("valeur", choices=[*STATUTS, "nouveau"])
    sub.add_parser("relances")
    rl = sub.add_parser("relancer")
    rl.add_argument("id", type=int)
    en = sub.add_parser("entretien")
    en.add_argument("id", type=int)
    w = sub.add_parser("web")
    w.add_argument("--port", type=int, default=8765)
    w.add_argument("--local", action="store_true", help="accessible depuis cet ordinateur seulement")
    args = p.parse_args(argv)

    if args.cmd == "web":
        from .web.serveur import lancer
        charger_env()
        lancer(port=args.port, local=args.local)
        return

    charger_env()
    db = Base()
    try:
        if args.cmd == "collecter":
            n = pipeline.collecter(db)
            print(f"\n{n} offres à noter. Lance : python -m jobbot noter")
        elif args.cmd == "noter":
            pipeline.noter_tout(db, Claude())
            _top(db, None)
        elif args.cmd == "go":
            chemins = pipeline.tout(db, Claude())
            _top(db, None)
            print(f"\n{len(chemins)} dossier(s) préparé(s) dans candidatures/. Relis-les avant d'envoyer.")
        elif args.cmd == "top":
            _top(db, args.min)
        elif args.cmd == "preparer":
            chemin = pipeline.preparer(db, Claude(), args.id, args.lettre)
            print(f"✓ Dossier prêt : {chemin}")
        elif args.cmd == "coller":
            texte = sys.stdin.read() if args.fichier == "-" else open(args.fichier, encoding="utf-8").read()
            if len(texte.strip()) < 100:
                raise SystemExit("Texte trop court : colle l'offre complète.")
            offre_id = pipeline.ajouter_a_la_main(db, texte, args.url)
            chemin = pipeline.preparer(db, Claude(), offre_id, args.lettre)
            note = db.note(offre_id)
            print(f"Offre #{offre_id} — score {note.score}/100 — {note.verdict}")
            print(f"✓ Dossier prêt : {chemin}")
        elif args.cmd == "statut":
            ok = db.changer_statut(args.id, args.valeur)
            print("✓ Statut mis à jour." if ok else "Offre inconnue.")
        elif args.cmd == "relances":
            jours = int(config().get("relance_apres_jours", 7))
            rows = db.relances_dues(jours)
            if not rows:
                print(f"Aucune candidature envoyée depuis plus de {jours} jours sans relance.")
            for r in rows:
                print(f"{r['id']:>4}  envoyée le {r['envoye_le'][:10]}  {r['titre'][:55]}")
            if rows:
                print("\nRédiger une relance : python -m jobbot relancer <n°>")
        elif args.cmd == "relancer":
            print(pipeline.relance(db, Claude(), args.id))
            db.marquer_relance(args.id)
        elif args.cmd == "entretien":
            print(pipeline.entretien(db, Claude(), args.id))
    finally:
        db.fermer()


def _top(db: Base, score_min: int | None) -> None:
    seuil = config().get("seuil", 70) if score_min is None else score_min
    rows = db.classement(seuil, expirees=False)
    if not rows:
        print(f"\nAucune offre notée ≥ {seuil}.")
        return
    print(f"\n{'N°':>4}  {'Score':>5}  {'Dossier':<9} Offre")
    for r in rows:
        d = detail_note(r)
        ent = d.get("entreprise") or r["entreprise"] or ""
        statut = r["statut"] or "—"
        print(f"{r['id']:>4}  {r['score']:>5}  {statut:<9} {r['titre'][:55]}" + (f" · {ent[:25]}" if ent else ""))
        if d.get("alerte"):
            print(f"{'':>17}⚠  {d['alerte']}")


if __name__ == "__main__":
    main()
