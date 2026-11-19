"""Les étapes du bot : collecter → noter → préparer (+ entretien, relance)."""
from __future__ import annotations

import hashlib
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, Optional

from . import coach, matcher, render, writer
from .config import config
from .db import Base
from .llm import LLM
from .models import Offre
from .sources import SOURCES
from .sources.base import Http, passe_le_filtre
from .sources.remotive import INTERVALLE_MIN

Log = Callable[[str], None]


def collecter(db: Base, http: Optional[Http] = None, log: Log = print) -> int:
    """Récupère les nouvelles offres de chaque source active. Renvoie le nombre retenu."""
    http = http or Http()
    retenues = 0
    for nom, conf in config().get("sources", {}).items():
        if not conf.get("actif") or nom not in SOURCES:
            continue
        if nom == "remotive" and time.time() - db.derniere_visite(nom) < INTERVALLE_MIN:
            log(f"· {nom} : déjà visité il y a moins de 6 h (règle Remotive), on passe.")
            continue
        source = SOURCES[nom](http, conf)
        nouvelles = gardees = doublons = 0
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
                        log(f"  ! détail illisible ({o.url}) : {err}")
                double = db.doublon(o) if ok else None
                if double:
                    doublons += 1
                    ok = False
                elif ok:
                    gardees += 1
                db.ajouter(o, filtre_ok=ok, doublon_de=double)
            db.marquer_visite(nom)
        except Exception as err:
            log(f"! {nom} : {err}")
        extra = f", {doublons} déjà vues ailleurs" if doublons else ""
        log(f"· {nom} : {nouvelles} nouvelles offres, {gardees} passent le filtre{extra}")
        retenues += gardees
    return retenues


def noter_tout(db: Base, llm: LLM, log: Log = print) -> int:
    """Note les offres en attente, plusieurs à la fois (config : parallele)."""
    offres = db.a_noter(int(config().get("max_offres_a_noter", 40)))
    if not offres:
        log("· rien à noter.")
        return 0
    paralleles = max(1, int(config().get("parallele", 4)))
    fait = 0
    with ThreadPoolExecutor(max_workers=paralleles) as pool:
        futurs = {pool.submit(matcher.noter, llm, o): o for o in offres}
        for f in as_completed(futurs):
            o = futurs[f]
            fait += 1
            try:
                note = f.result()
            except Exception as err:
                log(f"  ! #{o.id} non noté : {err}")
                continue
            db.noter(o.id, note)  # écriture dans le fil principal : SQLite reste simple
            alerte = f"  ⚠ {note.alerte}" if note.alerte else ""
            log(f"  [{fait}/{len(offres)}] #{o.id:<4} {note.score:>3}/100  {o.titre[:60]}{alerte}")
    return len(offres)


def preparer(db: Base, llm: LLM, offre_id: int, lettre: Optional[bool] = None) -> Path:
    o = db.offre(offre_id)
    if not o:
        raise SystemExit(f"Offre #{offre_id} inconnue.")
    note = db.note(offre_id)
    if not note:
        note = matcher.noter(llm, o)
        db.noter(offre_id, note)
    avec_lettre = note.lettre_demandee if lettre is None else lettre
    dossier = writer.rediger(llm, o, note, avec_lettre)
    chemin = render.generer(o, note, dossier)
    db.enregistrer_dossier(offre_id, chemin)
    return chemin


def tout(db: Base, llm: LLM, log: Log = print) -> list[Path]:
    """Collecte, note, puis prépare les dossiers des meilleures offres. N'envoie rien."""
    log("Collecte des offres…")
    collecter(db, log=log)
    log("Notation (Claude Haiku)…")
    noter_tout(db, llm, log=log)
    seuil = int(config().get("seuil", 70))
    ids = db.sans_dossier(seuil, int(config().get("max_dossiers", 5)))
    if ids:
        log(f"Rédaction de {len(ids)} dossier(s) (Claude Sonnet)…")
    chemins = []
    for offre_id in ids:
        try:
            chemins.append(preparer(db, llm, offre_id))
            log(f"  ✓ dossier prêt : #{offre_id}")
        except Exception as err:
            log(f"  ! #{offre_id} : {err}")
    db.ecrire_meta("dernier_go", time.strftime("%Y-%m-%dT%H:%M:%S"))
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


def _offre_et_note(db: Base, llm: LLM, offre_id: int):
    o = db.offre(offre_id)
    if not o:
        raise SystemExit(f"Offre #{offre_id} inconnue.")
    note = db.note(offre_id)
    if not note:
        note = matcher.noter(llm, o)
        db.noter(offre_id, note)
    return o, note


def entretien(db: Base, llm: LLM, offre_id: int) -> str:
    """Fiche de préparation d'entretien (Markdown), gardée en base et dans le dossier."""
    o, note = _offre_et_note(db, llm, offre_id)
    fiche = coach.preparer_entretien(llm, o, note)
    texte = coach.entretien_markdown(o, note, fiche)
    db.enregistrer_extra(offre_id, "entretien", fiche.model_dump_json())
    if chemin := db.dossier(offre_id):
        if chemin.exists():
            (chemin / "entretien.md").write_text(texte, encoding="utf-8")
    return texte


def relance(db: Base, llm: LLM, offre_id: int) -> str:
    """Message de relance après une candidature restée sans réponse."""
    o, note = _offre_et_note(db, llm, offre_id)
    s = db.suivi(offre_id)
    envoye_le = (s["envoye_le"] or "")[:10] if s else ""
    premier = ""
    if (chemin := db.dossier(offre_id)) and (chemin / "message.txt").exists():
        premier = (chemin / "message.txt").read_text(encoding="utf-8")
    r = coach.rediger_relance(llm, o, note, envoye_le, premier)
    a_qui = note.email_candidature or "(adresse non trouvée : voir l'offre)"
    texte = f"À : {a_qui}\nObjet : {r.objet}\n\n{r.texte}\n"
    db.enregistrer_extra(offre_id, "relance", texte)
    if chemin := db.dossier(offre_id):
        if chemin.exists():
            (chemin / "relance.txt").write_text(texte, encoding="utf-8")
    return texte
