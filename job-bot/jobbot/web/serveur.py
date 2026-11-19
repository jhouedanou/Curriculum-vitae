"""Interface web locale de JobBot : python -m jobbot web

Ouverte sur le Wi-Fi pour le téléphone, protégée par un jeton secret
(le lien complet s'affiche dans le terminal, avec un QR code).
"""
from __future__ import annotations

import json
import os
import secrets
import socket
import threading
import time
import traceback
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional
from urllib.parse import quote

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .. import pipeline
from ..config import config
from ..dates import date_publication, expiree, lire_date
from ..db import STATUTS, Base
from ..llm import Claude
from ..sources import SOURCES

ICI = Path(__file__).resolve().parent
COOKIE = "jobbot"

app = FastAPI(title="JobBot", docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=ICI / "static"), name="static")
vues = Jinja2Templates(directory=ICI / "templates")
app.state.jeton, app.state.port, app.state.local = "", 8765, True


# ── Jeton d'accès ───────────────────────────────────────────
def jeton() -> str:
    db = Base()
    try:
        t = db.lire_meta("web_token")
        if not t:
            t = secrets.token_urlsafe(18)
            db.ecrire_meta("web_token", t)
        return t
    finally:
        db.fermer()


@app.middleware("http")
async def verifier_jeton(request: Request, call_next):
    if request.url.path.startswith("/static/"):
        return await call_next(request)
    attendu = app.state.jeton
    donne = request.query_params.get("t")
    if donne and secrets.compare_digest(donne, attendu):
        # Lien du terminal : on pose le cookie puis on retire le jeton de l'adresse.
        r = RedirectResponse(request.url.path, status_code=303)
        r.set_cookie(COOKIE, attendu, max_age=60 * 60 * 24 * 180, httponly=True, samesite="strict")
        return r
    if not secrets.compare_digest(request.cookies.get(COOKIE, ""), attendu):
        return HTMLResponse(vues.get_template("acces.html").render(), status_code=401)
    return await call_next(request)


# ── Tâches de fond (une seule à la fois : la facture API reste lisible) ──
@dataclass
class Tache:
    id: str
    titre: str
    lien: str = ""                  # où aller quand c'est fini
    etat: str = "en_cours"          # en_cours, ok, erreur
    lignes: list[str] = field(default_factory=list)
    debut: float = field(default_factory=time.time)
    fin: Optional[float] = None

    def log(self, texte: str) -> None:
        self.lignes.append(str(texte))

    def vue(self) -> dict:
        return {"id": self.id, "titre": self.titre, "lien": self.lien, "etat": self.etat,
                "lignes": self.lignes[-400:], "duree": round((self.fin or time.time()) - self.debut)}


TACHES: dict[str, Tache] = {}
VERROU = threading.Lock()


def tache_en_cours() -> Optional[Tache]:
    return next((t for t in TACHES.values() if t.etat == "en_cours"), None)


def lancer_tache(titre: str, lien: str, travail: Callable[[Base, Callable[[str], None]], Optional[str]]) -> Tache:
    with VERROU:
        if (t := tache_en_cours()):
            raise HTTPException(409, f"Une tâche tourne déjà : {t.titre}")
        t = Tache(id=uuid.uuid4().hex[:10], titre=titre, lien=lien)
        TACHES[t.id] = t

    def courir():
        db = Base()
        try:
            fin = travail(db, t.log)
            if fin:
                t.lien = fin
            t.etat = "ok"
            t.log("Terminé.")
        except BaseException as err:  # SystemExit (clé absente…) compris
            t.etat = "erreur"
            t.log(f"Erreur : {err}")
            if not isinstance(err, SystemExit):
                traceback.print_exc()
        finally:
            t.fin = time.time()
            db.fermer()

    threading.Thread(target=courir, daemon=True).start()
    return t


def exiger_cle() -> None:
    if not cle_api():
        raise HTTPException(412, "Cette action utilise Claude : ajoute ANTHROPIC_API_KEY=sk-ant-… dans le fichier .env "
                                 "du dossier job-bot, puis relance python -m jobbot web.")


def reponse_tache(request: Request, t: Tache) -> Response:
    if request.headers.get("accept", "").startswith("application/json"):
        return JSONResponse(t.vue())
    return RedirectResponse(f"/taches/{t.id}", status_code=303)


# ── Aides de présentation ────────────────────────────────────
def _il_y_a(iso: Optional[str]) -> str:
    if not iso:
        return "jamais"
    try:
        d = datetime.fromisoformat(iso)
    except ValueError:
        return iso
    s = (datetime.now() - d).total_seconds()
    if s < 3600:
        return f"il y a {max(1, int(s // 60))} min"
    if s < 86400:
        return f"il y a {int(s // 3600)} h"
    j = int(s // 86400)
    return "hier" if j == 1 else f"il y a {j} jours"


def _jours_restants(date_limite: Optional[str]) -> Optional[int]:
    d = lire_date(date_limite)
    return (d - datetime.now().date()).days if d else None


def _carte(r) -> dict:
    d = json.loads(r["detail"])
    return {
        "id": r["id"], "titre": d.get("intitule") or r["titre"], "score": r["score"],
        "entreprise": d.get("entreprise") or r["entreprise"] or "", "lieu": r["lieu"] or "",
        "source": r["source"], "statut": r["statut"] or "nouveau", "dossier": bool(r["chemin"]),
        "verdict": d.get("verdict", ""), "alerte": d.get("alerte"), "lettre": d.get("lettre_demandee"),
        "date_limite": d.get("date_limite"), "jours": _jours_restants(d.get("date_limite")),
        "expiree": expiree(d.get("date_limite")), "vue_le": r["vue_le"],
    }


def cle_api() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def _commun(request: Request, db: Base, actif: str) -> dict:
    return {"request": request, "actif": actif, "STATUTS": STATUTS, "tache": tache_en_cours(),
            "nb_relire": db.compter_statuts().get("a_relire", 0), "cle_api": cle_api()}


def _brute(r) -> dict:
    """Offre pas encore notée."""
    pub = date_publication(r["publie_le"], r["vue_le"])
    return {
        "id": r["id"], "titre": r["titre"], "entreprise": r["entreprise"] or "", "lieu": r["lieu"] or "",
        "source": r["source"], "url": r["url"] or "", "statut": r["statut"] or "nouveau",
        "filtre_ok": bool(r["filtre_ok"]), "publie": pub,
        "age": (datetime.now().date() - pub).days if pub else None,
        "extrait": " ".join((r["description"] or "").split())[:220],
    }


vues.env.globals.update(il_y_a=_il_y_a)


# ── Pages ───────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def accueil(request: Request, vue: str = "", source: str = "", q: str = "", periode: str = "21",
            tout: bool = False):
    from ..sources.base import normaliser

    db = Base()
    try:
        seuil = int(config().get("seuil", 70))
        # Sans clé API, rien n'est noté : on montre d'abord les offres collectées.
        vue = vue or ("a_traiter" if cle_api() else "a_noter")
        if vue == "a_noter":
            cartes = [_brute(r) for r in db.non_notees(500, hors_filtre=tout)]
            if periode.isdigit():
                cartes = [c for c in cartes if c["age"] is None or c["age"] <= int(periode)]
            cartes.sort(key=lambda c: c["publie"] or datetime.min.date(), reverse=True)
        else:
            if vue == "toutes":
                rows = db.classement(0, 500)
            elif vue == "proches":  # sous le seuil mais pas hors sujet
                rows = [r for r in db.classement(50, 300, expirees=False, statuts=["nouveau", "a_relire"])
                        if r["score"] < seuil]
            else:
                vue = "a_traiter"
                rows = db.classement(seuil, 200, expirees=False, statuts=["nouveau", "a_relire"])
            cartes = [_carte(r) for r in rows]
        if source:
            cartes = [c for c in cartes if c["source"] == source]
        if q:
            k = normaliser(q)
            cartes = [c for c in cartes if k in normaliser(f"{c['titre']} {c['entreprise']} {c['lieu']}")]
        jours = int(config().get("relance_apres_jours", 7))
        relances = [{"id": r["id"], "titre": r["titre"], "entreprise": r["entreprise"] or "",
                     "envoye_le": r["envoye_le"]} for r in db.relances_dues(jours)]
        visites = {nom: db.derniere_visite(nom) for nom in SOURCES}
        derniere = max(visites.values() or [0])
        return vues.TemplateResponse(request, "offres.html", {
            **_commun(request, db, "offres"), "cartes": cartes, "vue": vue, "source": source, "q": q,
            "periode": periode, "tout": tout,
            "seuil": seuil, "relances": relances, "jours_relance": jours, "a_noter": db.nb_a_noter(),
            "derniere": datetime.fromtimestamp(derniere).isoformat() if derniere else None,
            "sources": list(SOURCES) + ["manuel"],
        })
    finally:
        db.fermer()


@app.get("/offre/{offre_id}", response_class=HTMLResponse)
def page_offre(request: Request, offre_id: int):
    db = Base()
    try:
        o = db.offre(offre_id)
        if not o:
            raise HTTPException(404, "Offre inconnue")
        note = db.note(offre_id)
        chemin = db.dossier(offre_id)
        fichiers, message, dossier = {}, None, None
        if chemin and chemin.exists():
            fichiers = {p.name: p for p in sorted(chemin.iterdir()) if p.is_file()}
            if "message.txt" in fichiers:
                message = _lire_message(fichiers["message.txt"].read_text(encoding="utf-8"))
            if "dossier.json" in fichiers:
                dossier = json.loads(fichiers["dossier.json"].read_text(encoding="utf-8"))
        s = db.suivi(offre_id)
        entretien = db.extra(offre_id, "entretien")
        relance = db.extra(offre_id, "relance")
        return vues.TemplateResponse(request, "offre.html", {
            **_commun(request, db, "offres"), "o": o, "n": note, "fichiers": fichiers, "message": message,
            "dossier": dossier, "statut": s["statut"] if s else "nouveau", "suivi": s,
            "entretien": json.loads(entretien) if entretien else None,
            "relance": _lire_message(relance) if relance else None,
            "jours": _jours_restants(note.date_limite) if note else None,
            "expiree": expiree(note.date_limite) if note else False,
        })
    finally:
        db.fermer()


def _lire_message(texte: str) -> dict:
    """« À : …\\nObjet : …\\n\\ncorps » → dict."""
    tete, _, corps = texte.partition("\n\n")
    m = {"a": "", "objet": "", "texte": corps.strip()}
    for ligne in tete.splitlines():
        if ligne.startswith("À :"):
            m["a"] = ligne[3:].strip()
        elif ligne.startswith("Objet :"):
            m["objet"] = ligne[7:].strip()
    m["email"] = m["a"] if "@" in m["a"] and " " not in m["a"] else ""
    m["mailto"] = (f"mailto:{m['email']}?subject={quote(m['objet'])}&body={quote(m['texte'])}"
                   if m["email"] else "")
    return m


@app.get("/suivi", response_class=HTMLResponse)
def page_suivi(request: Request):
    db = Base()
    try:
        cartes = [_carte(r) for r in db.classement(0, 1000) if r["statut"]]
        colonnes = {k: [c for c in cartes if c["statut"] == k] for k in STATUTS}
        jours = int(config().get("relance_apres_jours", 7))
        dues = {r["id"] for r in db.relances_dues(jours)}
        return vues.TemplateResponse(request, "suivi.html", {
            **_commun(request, db, "suivi"), "colonnes": colonnes, "dues": dues,
        })
    finally:
        db.fermer()


@app.get("/coller", response_class=HTMLResponse)
def page_coller(request: Request):
    db = Base()
    try:
        return vues.TemplateResponse(request, "coller.html", {**_commun(request, db, "coller"), "erreur": None})
    finally:
        db.fermer()


@app.post("/coller")
def action_coller(request: Request, texte: str = Form(...), url: str = Form(""), lettre: str = Form("auto")):
    if not cle_api():
        db = Base()
        try:
            return vues.TemplateResponse(request, "coller.html", {
                **_commun(request, db, "coller"), "texte": texte, "url": url,
                "erreur": "Sans clé API, le bot ne peut pas analyser l'offre. Ajoute ANTHROPIC_API_KEY dans job-bot/.env.",
            }, status_code=412)
        finally:
            db.fermer()
    if len(texte.strip()) < 100:
        db = Base()
        try:
            return vues.TemplateResponse(request, "coller.html", {
                **_commun(request, db, "coller"), "texte": texte, "url": url,
                "erreur": "Le texte est trop court : colle l'offre complète (missions, profil, comment postuler).",
            }, status_code=422)
        finally:
            db.fermer()
    db = Base()
    try:
        offre_id = pipeline.ajouter_a_la_main(db, texte, url.strip())
    finally:
        db.fermer()
    avec = {"oui": True, "non": False}.get(lettre)

    def travail(db, log):
        log("Analyse de l'offre et rédaction du dossier (Claude)…")
        pipeline.preparer(db, Claude(), offre_id, avec)
        n = db.note(offre_id)
        log(f"Score {n.score}/100 — {n.verdict}")

    return reponse_tache(request, lancer_tache("Offre collée : dossier", f"/offre/{offre_id}", travail))


@app.get("/taches/{tid}", response_class=HTMLResponse)
def page_tache(request: Request, tid: str):
    t = TACHES.get(tid)
    if not t:
        return RedirectResponse("/", status_code=303)
    db = Base()
    try:
        return vues.TemplateResponse(request, "tache.html", {**_commun(request, db, ""), "t": t})
    finally:
        db.fermer()


# ── Actions ─────────────────────────────────────────────────
@app.post("/lancer")
def action_lancer(request: Request, quoi: str = Form("go")):
    if quoi != "collecter":
        exiger_cle()
    if quoi == "collecter":
        def travail(db, log):
            n = pipeline.collecter(db, log=log)
            log(f"{n} offre(s) à noter.")
        titre = "Collecte des offres"
    elif quoi == "noter":
        def travail(db, log):
            pipeline.noter_tout(db, Claude(), log=log)
        titre = "Notation des offres"
    else:
        def travail(db, log):
            chemins = pipeline.tout(db, Claude(), log=log)
            log(f"{len(chemins)} dossier(s) préparé(s). Relis-les avant d'envoyer.")
        titre = "Recherche du jour"
    return reponse_tache(request, lancer_tache(titre, "/", travail))


@app.post("/offre/{offre_id}/preparer")
def action_preparer(request: Request, offre_id: int, lettre: str = Form("auto")):
    exiger_cle()
    avec = {"oui": True, "non": False}.get(lettre)

    def travail(db, log):
        log("Rédaction du CV et du message" + (", avec lettre" if avec else "") + " (Claude Sonnet)…")
        pipeline.preparer(db, Claude(), offre_id, avec)

    return reponse_tache(request, lancer_tache(f"Dossier de l'offre #{offre_id}", f"/offre/{offre_id}", travail))


@app.post("/offre/{offre_id}/entretien")
def action_entretien(request: Request, offre_id: int):
    exiger_cle()
    def travail(db, log):
        log("Questions probables, réponses STAR, questions à poser (Claude Sonnet)…")
        pipeline.entretien(db, Claude(), offre_id)

    return reponse_tache(request, lancer_tache(
        f"Préparation d'entretien #{offre_id}", f"/offre/{offre_id}#entretien", travail))


@app.post("/offre/{offre_id}/relance")
def action_relance(request: Request, offre_id: int):
    exiger_cle()
    def travail(db, log):
        log("Rédaction de la relance (Claude Sonnet)…")
        pipeline.relance(db, Claude(), offre_id)

    return reponse_tache(request, lancer_tache(f"Relance #{offre_id}", f"/offre/{offre_id}#relance", travail))


@app.post("/offre/{offre_id}/statut")
def action_statut(request: Request, offre_id: int, statut: str = Form(...), retour: str = Form("")):
    db = Base()
    try:
        if statut not in STATUTS and statut != "nouveau":
            raise HTTPException(400, "Statut inconnu")
        if not db.changer_statut(offre_id, statut):
            raise HTTPException(404, "Offre inconnue")
    finally:
        db.fermer()
    if request.headers.get("accept", "").startswith("application/json"):
        return JSONResponse({"ok": True, "statut": statut})
    return RedirectResponse(retour if retour.startswith("/") else f"/offre/{offre_id}", status_code=303)


@app.post("/offre/{offre_id}/relance-faite")
def action_relance_faite(request: Request, offre_id: int):
    db = Base()
    try:
        db.marquer_relance(offre_id)
    finally:
        db.fermer()
    if request.headers.get("accept", "").startswith("application/json"):
        return JSONResponse({"ok": True})
    return RedirectResponse(f"/offre/{offre_id}", status_code=303)


@app.get("/api/taches/{tid}")
def api_tache(tid: str):
    t = TACHES.get(tid)
    if not t:
        raise HTTPException(404, "Tâche inconnue")
    return t.vue()


@app.get("/fichiers/{offre_id}/{nom}")
def fichier(offre_id: int, nom: str, telecharger: bool = False):
    db = Base()
    try:
        chemin = db.dossier(offre_id)
    finally:
        db.fermer()
    if not chemin or not chemin.exists():
        raise HTTPException(404)
    p = (chemin / nom).resolve()
    if p.parent != chemin.resolve() or not p.is_file():  # pas de sortie du dossier
        raise HTTPException(404)
    return FileResponse(p, filename=nom if telecharger else None,
                        content_disposition_type="attachment" if telecharger else "inline")


@app.get("/telephone", response_class=HTMLResponse)
def page_telephone(request: Request):
    db = Base()
    try:
        lien = f"http://{ip_locale()}:{app.state.port}/?t={app.state.jeton}" if not app.state.local else ""
        svg = ""
        if lien:
            try:
                import segno
                svg = segno.make(lien, error="m").svg_inline(scale=6, dark="currentColor", light=None)
            except ImportError:
                pass
        return vues.TemplateResponse(request, "telephone.html", {**_commun(request, db, ""), "lien": lien, "svg": svg})
    finally:
        db.fermer()


@app.exception_handler(HTTPException)
async def erreur_http(request: Request, exc: HTTPException):
    if request.headers.get("accept", "").startswith("application/json"):
        return JSONResponse({"erreur": exc.detail}, status_code=exc.status_code)
    db = Base()
    try:
        return vues.TemplateResponse(request, "erreur.html", {**_commun(request, db, ""), "code": exc.status_code,
                                                              "message": exc.detail}, status_code=exc.status_code)
    finally:
        db.fermer()


# ── Lancement ───────────────────────────────────────────────
def ip_locale() -> str:
    """Adresse de l'ordinateur sur le Wi-Fi (aucun paquet n'est envoyé)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def lancer(port: int = 8765, local: bool = False) -> None:
    import uvicorn

    app.state.jeton = jeton()
    app.state.port = port
    app.state.local = local
    hote = "127.0.0.1" if local else "0.0.0.0"
    print(f"\n  JobBot  ·  http://127.0.0.1:{port}/?t={app.state.jeton}")
    if not local:
        lien = f"http://{ip_locale()}:{port}/?t={app.state.jeton}"
        print(f"  Téléphone (même Wi-Fi)  ·  {lien}")
        try:
            import segno
            segno.make(lien, error="m").terminal(compact=True)
        except ImportError:
            pass
        print("  Garde ce lien pour toi : il donne accès à tes candidatures.\n")
    uvicorn.run(app, host=hote, port=port, log_level="warning")
