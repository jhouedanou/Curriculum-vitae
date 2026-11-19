"""Les étapes du bot : collecter → noter → préparer."""
from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Optional

from . import matcher, render, writer
from .config import config
from .db import Base
from .llm import LLM
from .models import Offre
from .sources import SOURCES
from .sources.base import Http, passe_le_filtre
from .sources.remotive import INTERVALLE_MIN


def collecter(db: Base, http: Optional[Http] = None) -> int:
    """Récupère les nouvelles offres de chaque source active. Renvoie le nombre retenu."""
    http = http or Http()
    retenues = 0
    for nom, conf in config().get("sources", {}).items():
        if not conf.get("actif") or nom not in SOURCES:
            continue
        if nom == "remotive" and time.time() - db.derniere_visite(nom) < INTERVALLE_MIN:
            print(f"· {nom} : déjà visité il y a moins de 6 h (règle Remotive), on passe.")
            continue
        source = SOURCES[nom](http, conf)
        nouvelles = gardees = 0
        try:
            for o in source.offres():
                if db.existe(o.source, o.ref):
                    continue
                nouvelles += 1
                ok = passe_le_filtre(o)
                if ok:
                    try:
                        o = source.completer(o)
                    except Exception as err:
                        print(f"  ! détail illisible ({o.url}) : {err}")
                    gardees += 1
                db.ajouter(o, filtre_ok=ok)
            db.marquer_visite(nom)
        except Exception as err:
            print(f"! {nom} : {err}")
        print(f"· {nom} : {nouvelles} nouvelles offres, {gardees} passent le filtre")
        retenues += gardees
    return retenues


def noter_tout(db: Base, llm: LLM) -> int:
    offres = db.a_noter(int(config().get("max_offres_a_noter", 40)))
    for i, o in enumerate(offres, 1):
        try:
            note = matcher.noter(llm, o)
        except Exception as err:
            print(f"  ! #{o.id} non noté : {err}")
            continue
        db.noter(o.id, note)
        alerte = f"  ⚠️ {note.alerte}" if note.alerte else ""
        print(f"  [{i}/{len(offres)}] #{o.id:<4} {note.score:>3}/100  {o.titre[:60]}{alerte}")
    return len(offres)


def preparer(db: Base, llm: LLM, offre_id: int, lettre: Optional[bool] = None) -> Path:
    o = db.offre(offre_id)
    if not o:
        raise SystemExit(f"Offre #{offre_id} inconnue.")
    note = db.note(offre_id) or matcher.noter(llm, o)
    db.noter(offre_id, note)
    avec_lettre = note.lettre_demandee if lettre is None else lettre
    dossier = writer.rediger(llm, o, note, avec_lettre)
    chemin = render.generer(o, note, dossier)
    db.enregistrer_dossier(offre_id, chemin)
    return chemin


def tout(db: Base, llm: LLM) -> list[Path]:
    """Collecte, note, puis prépare les dossiers des meilleures offres. N'envoie rien."""
    collecter(db)
    noter_tout(db, llm)
    seuil = int(config().get("seuil", 70))
    chemins = []
    for offre_id in db.sans_dossier(seuil, int(config().get("max_dossiers", 5))):
        try:
            chemins.append(preparer(db, llm, offre_id))
            print(f"  ✓ dossier prêt : {chemins[-1]}")
        except Exception as err:
            print(f"  ! #{offre_id} : {err}")
    return chemins


def ajouter_a_la_main(db: Base, texte: str, url: str = "") -> int:
    """Offre collée à la main (LinkedIn, email, WhatsApp…)."""
    premiere = next((l.strip() for l in texte.splitlines() if l.strip()), "Offre collée")
    ref = hashlib.sha1(texte.encode("utf-8")).hexdigest()[:12]
    o = Offre(source="manuel", ref=ref, titre=premiere[:120], url=url, description=texte)
    offre_id = db.ajouter(o)
    if offre_id is None:
        offre_id = db.cx.execute("SELECT id FROM offres WHERE source='manuel' AND ref=?", (ref,)).fetchone()[0]
    return offre_id
