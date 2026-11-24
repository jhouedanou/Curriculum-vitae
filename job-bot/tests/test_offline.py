"""Tests sans Internet ni clé API : python -m pytest -q"""
from __future__ import annotations

import time
from pathlib import Path

import pytest

from jobbot import pipeline, render
from jobbot.db import Base
from jobbot.dates import expiree, lire_date
from jobbot.models import (CVAdapte, Exigence, ExperienceAdaptee, Lettre, Manque, Message, Note, Offre,
                           PreparationEntretien, QuestionProbable, Relance, Salaire, TrameSTAR, lire_note)
from jobbot.sources.base import passe_le_filtre
from jobbot.sources.educarriere import lire_liste
from jobbot.sources.novojob import lire_flux
from jobbot.sources.remotive import lire_json
from jobbot.writer import _Reponse

RSS = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0"><channel><title>Novojob</title><link>https://www.novojob.com</link><description>x</description>
<item><title>: Développeur Full-Stack VueJS / Laravel</title>
<link>https://www.novojob.com/cote-d-ivoire/offres-d-emploi/offre-d-emploi/cote-d-ivoire/abidjan/136900-developpeur-full-stack</link>
<guid isPermaLink="true">https://www.novojob.com/cote-d-ivoire/offres-d-emploi/offre-d-emploi/cote-d-ivoire/abidjan/136900-developpeur-full-stack</guid>
<description><![CDATA[<p>Nous recherchons un développeur <b>senior</b>.</p><ul><li>VueJS</li><li>Laravel</li></ul>]]></description>
<pubDate>Mon, 05 Oct 2026 11:20:44 +0100</pubDate></item>
<item><title>Comptable confirmé</title>
<link>https://www.novojob.com/cote-d-ivoire/offres-d-emploi/offre-d-emploi/cote-d-ivoire/136901-comptable</link>
<guid>x</guid><description>Compta</description><pubDate>Mon, 05 Oct 2026 11:20:44 +0100</pubDate></item>
</channel></rss>"""

EDUCARRIERE = """<html><body>
<a href="offre-156700-chef-de-projet-digital.html"><img src="logo.png"></a>
<a href="offre-156700-chef-de-projet-digital.html">CHEF DE PROJET DIGITAL</a>
<a href="https://emploi.educarriere.ci/offre-156701-assistant-e-comptable.html">ASSISTANT(E) COMPTABLE</a>
<a href="offre-156702-developpeur-web.html">Développeur Web Vue.js ACME SA Limite : 27/11/2026 emploi</a>
<a href="/page/all">Toutes les offres</a>
</body></html>"""

REMOTIVE = {"jobs": [
    {"id": 1, "url": "https://remotive.com/1", "title": "Senior Vue.js Developer", "company_name": "Acme",
     "candidate_required_location": "Worldwide", "publication_date": "2026-10-01", "description": "<p>Vue 3</p>"},
    {"id": 2, "url": "https://remotive.com/2", "title": "React Dev", "company_name": "Beta",
     "candidate_required_location": "USA Only", "publication_date": "2026-10-01", "description": "<p>x</p>"},
]}

OFFRE_TEXTE = """Développeur Front-End Senior (VueJS) — Banque XYZ, Abidjan
Missions : concevoir des interfaces VueJS, encadrer 2 développeurs, travailler avec l'équipe UX.
Profil : 7 ans d'expérience, VueJS, Nuxt, API REST, Figma. Anglais lu.
Dossier : CV + lettre de motivation à envoyer à recrutement@xyz.ci avant le 30/10/2026."""


def note_test(**kw) -> Note:
    base = dict(score=88, verdict="Très bon profil.", recommandation="postuler", points_forts=["VueJS expert"],
                ecarts=["Secteur bancaire"],
                exigences=[Exigence(intitule="VueJS", indispensable=True, couvert="oui", preuve_cv="Big Five")],
                manques=[Manque(intitule="Secteur bancaire", gravite="mineur", strategie="—")],
                mots_cles_absents=["Angular"], arguments_forts=["12 ans de web"], signaux=[],
                surqualification=False, seniorite="senior", type_contrat="CDI", mode_travail="sur site",
                salaire=None, entreprise="Banque XYZ", intitule="Développeur Front-End Senior", langue="fr",
                lettre_demandee=True, email_candidature="recrutement@xyz.ci", date_limite="30/10/2099",
                consignes="CV + lettre", alerte=None)
    return Note(**{**base, **kw})


class FauxClaude:
    """Remplace Claude dans les tests : réponses fixes, avec des erreurs volontaires."""

    def demander(self, modele, systeme, cv, consigne, format, max_tokens=4000):
        if format is Note:
            return note_test()
        if format is PreparationEntretien:
            return PreparationEntretien(
                competences_evaluees=["VueJS — « maîtrise de VueJS »"], pitch="Je suis…",
                questions=[QuestionProbable(question="Parlez d'un projet VueJS", categorie="technique",
                                            probabilite="haute", conseil=None,
                                            star=TrameSTAR(situation="s", tache="t", action="a", resultat="r",
                                                           experience_source="Big Five"))],
                points_faibles=[], questions_a_poser=["Quels défis ?"],
                salaire=Salaire(fourchette_offre=None, strategie="Demander la fourchette.", arguments=[],
                                negociable=["télétravail"], phrases=[]),
                a_eviter=[], a_verifier=[])
        if format is Relance:
            return Relance(objet="Re : candidature", texte="Bonjour, …", element_nouveau="portfolio")
        assert format is _Reponse
        return _Reponse(
            cv=CVAdapte(
                titre="Développeur front-end senior · VueJS",
                resume="12 ans de développement web, dont 5 ans en VueJS.",
                competences=["VueJS", "NuxtJS", "Kubernetes", "Figma", "APIs RESTful"],  # Kubernetes = invention
                experiences=[ExperienceAdaptee(id="bigfive", puces=["Lancé 17+ projets web, +40 % de trafic",
                                                                    "Réduit le temps de chargement de 73 %"]),  # 73 = invention
                             ExperienceAdaptee(id="inconnue", puces=["x"])],
                projets=["vodacom", "eatisfamily", "projet-fantome"],
            ),
            lettre=Lettre(objet="Développeur Front-End Senior", destinataire="Service Recrutement — Banque XYZ",
                          paragraphes=["Para 1.", "Para 2.", "Para 3.", "Para 4."]),
            message=Message(objet_email="Candidature — Développeur Front-End Senior",
                            texte="Bonjour, … Jean-Luc Houédanou"),
            a_completer=["Combien d'utilisateurs ?"],
        )


def test_rss_novojob():
    offres = list(lire_flux(RSS))
    assert offres[0].ref == "136900"
    assert offres[0].titre == "Développeur Full-Stack VueJS / Laravel"
    assert offres[0].lieu == "Abidjan"
    assert "Laravel" in offres[0].description
    assert passe_le_filtre(offres[0]) and not passe_le_filtre(offres[1])


def test_liste_educarriere():
    offres = list(lire_liste(EDUCARRIERE))
    assert [o.ref for o in offres] == ["156700", "156701", "156702"]
    assert offres[2].titre == "Développeur Web Vue.js ACME SA"
    assert offres[2].description == "Date limite : 27/11/2026"
    assert offres[0].titre == "CHEF DE PROJET DIGITAL"
    assert offres[0].url == "https://emploi.educarriere.ci/offre-156700-chef-de-projet-digital.html"
    assert passe_le_filtre(offres[0]) and not passe_le_filtre(offres[1])


def test_remotive_filtre_lieu():
    offres = list(lire_json(REMOTIVE, ["worldwide", "africa"]))
    assert [o.ref for o in offres] == ["1"]
    assert offres[0].description.endswith("Source : Remotive")


def test_filtre_mots_entiers():
    # « stage » exclu, mais pas « stagnation » ; « vue » seul (« point de vue ») ne suffit pas
    assert not passe_le_filtre(Offre(source="t", ref="1", titre="Stage développeur web"))
    assert not passe_le_filtre(Offre(source="t", ref="2", titre="Chargé de clientèle", description="point de vue"))
    assert passe_le_filtre(Offre(source="t", ref="3", titre="Lead Tech Nuxt"))


class FauxHttp:
    """Répond comme les vrais sites, sans réseau."""

    class R:
        def __init__(self, texte="", data=None):
            self.text, self.content, self._data = texte, texte.encode(), data

        def json(self):
            return self._data

    def get(self, url, **kw):
        if url.endswith("/rss"):
            return self.R(RSS)
        if "remotive.com/api" in url:
            return self.R(data=REMOTIVE)
        if url == "https://emploi.educarriere.ci/":
            return self.R(EDUCARRIERE)
        if "educarriere.ci/page/all" in url:
            return self.R(EDUCARRIERE)  # même page : le bot doit s'arrêter
        return self.R("<html><body><article><p>" + "Missions : VueJS, Nuxt, équipe. " * 30 + "</p></article></body></html>")


def test_collecte(tmp_path: Path):
    db = Base(tmp_path / "test.db")
    assert pipeline.collecter(db, FauxHttp()) == 4      # 1 Novojob + 2 Educarrière + 1 Remotive
    assert pipeline.collecter(db, FauxHttp()) == 0      # rien de nouveau au 2e passage
    a_noter = db.a_noter(10)
    assert len(a_noter) == 4
    edu = next(o for o in a_noter if o.ref == "156700")
    assert "VueJS" in edu.description                    # page de détail lue
    dev = next(o for o in a_noter if o.ref == "156702")
    assert "Date limite : 27/11/2026" in dev.description  # gardée après lecture du détail
    db.fermer()


def test_dossier_complet(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(render, "SORTIE", tmp_path / "candidatures")
    db = Base(tmp_path / "test.db")
    offre_id = pipeline.ajouter_a_la_main(db, OFFRE_TEXTE)
    assert pipeline.ajouter_a_la_main(db, OFFRE_TEXTE) == offre_id  # pas de doublon

    chemin = pipeline.preparer(db, FauxClaude(), offre_id)
    fichiers = {p.name for p in chemin.iterdir()}
    assert {"CV_Jean_Luc_Houedanou.html", "CV_Jean_Luc_Houedanou.pdf",
            "Lettre_Jean_Luc_Houedanou.html", "Lettre_Jean_Luc_Houedanou.pdf",
            "message.txt", "offre.md"} <= fichiers

    cv_html = (chemin / "CV_Jean_Luc_Houedanou.html").read_text(encoding="utf-8")
    assert "Kubernetes" not in cv_html            # compétence inventée retirée
    assert "WeDev Group" in cv_html               # expérience oubliée par l'IA remise
    assert "projet-fantome" not in cv_html
    fiche = (chemin / "offre.md").read_text(encoding="utf-8")
    assert "Kubernetes" in fiche and "« 73 »" in fiche   # signalés dans « À vérifier »
    assert "recrutement@xyz.ci" in (chemin / "message.txt").read_text(encoding="utf-8")
    assert db.classement(80)[0]["statut"] == "a_relire"

    # Sorties pour les logiciels de tri (ATS) : Markdown + PDF, une colonne, sans image ni tableau
    assert {"CV_ATS_Jean_Luc_Houedanou.md", "CV_ATS_Jean_Luc_Houedanou.html", "CV_ATS_Jean_Luc_Houedanou.pdf",
            "Lettre_Jean_Luc_Houedanou.md", "Email_Jean_Luc_Houedanou.md"} <= fichiers
    ats_html = (chemin / "CV_ATS_Jean_Luc_Houedanou.html").read_text(encoding="utf-8")
    assert "<img" not in ats_html and "<table" not in ats_html
    ats_md = (chemin / "CV_ATS_Jean_Luc_Houedanou.md").read_text(encoding="utf-8")
    assert ats_md.startswith("# Jean-Luc Houédanou") and "<" not in ats_md and "|---" not in ats_md
    for titre in ("## Profil professionnel", "## Compétences", "## Expérience professionnelle", "## Formation"):
        assert titre in ats_md
    assert "WeDev Group" in ats_md and "Kubernetes" not in ats_md      # mêmes garde-fous que le CV mis en page
    assert "Email : " in ats_md and "Téléphone : " in ats_md
    lettre_md = (chemin / "Lettre_Jean_Luc_Houedanou.md").read_text(encoding="utf-8")
    assert "## Objet : Développeur Front-End Senior" in lettre_md and "Para 4." in lettre_md
    email_md = (chemin / "Email_Jean_Luc_Houedanou.md").read_text(encoding="utf-8")
    assert "recrutement@xyz.ci" in email_md and "Candidature — Développeur Front-End Senior" in email_md

    # Dossier refait sans lettre : l'ancienne lettre disparaît
    chemin = pipeline.preparer(db, FauxClaude(), offre_id, lettre=False)
    assert not (chemin / "Lettre_Jean_Luc_Houedanou.md").exists()
    assert not (chemin / "Lettre_Jean_Luc_Houedanou.pdf").exists()
    db.fermer()


PAGE_OFFRE = """<html><head><title>Emploi | ACME</title><meta property="og:title" content="Développeur Front-End Senior — ACME">
</head><body><nav>Accueil Offres Contact</nav><main><h1>Développeur Front-End Senior</h1>
<p>""" + " ".join(["ACME recrute un développeur VueJS pour concevoir les interfaces de sa banque en ligne."] * 8) + """</p>
<ul><li>7 ans d'expérience</li><li>VueJS, Nuxt, API REST</li></ul></main><footer>Mentions légales</footer></body></html>"""


class FauxPage:
    def __init__(self, html: str):
        self.html, self.appels = html, []

    def get(self, url, **kw):
        self.appels.append(url)
        return type("R", (), {"text": self.html})()


def test_offre_par_lien(tmp_path: Path):
    from jobbot.lien import LienIllisible, lire_offre, verifier_lien

    titre, texte = lire_offre("https://acme.ci/emploi/42", FauxPage(PAGE_OFFRE))
    assert titre == "Développeur Front-End Senior — ACME"
    assert "banque en ligne" in texte and "Mentions légales" not in texte

    db = Base(tmp_path / "test.db")
    http = FauxPage(PAGE_OFFRE)
    offre_id = pipeline.ajouter_par_lien(db, "https://acme.ci/emploi/42", http, log=lambda _: None)
    o = db.offre(offre_id)
    assert o.source == "manuel" and o.url == "https://acme.ci/emploi/42" and o.titre.startswith("Développeur")
    assert pipeline.ajouter_par_lien(db, "https://acme.ci/emploi/42", http, log=lambda _: None) == offre_id
    db.fermer()

    for mauvais in ("acme.ci/emploi", "ftp://acme.ci/x", "http://localhost:8000/x", "http://192.168.1.10/x",
                    "https://www.linkedin.com/jobs/view/1", "https://fr.indeed.com/viewjob?jk=1"):
        with pytest.raises(LienIllisible):
            verifier_lien(mauvais)
    with pytest.raises(LienIllisible):                       # page presque vide (annonce chargée en JavaScript)
        lire_offre("https://acme.ci/emploi/43", FauxPage("<html><body><div id='app'></div></body></html>"))
    aucun_appel = FauxPage(PAGE_OFFRE)
    with pytest.raises(LienIllisible):                       # site refusé : aucune requête ne part
        lire_offre("https://www.linkedin.com/jobs/view/1", aucun_appel)
    assert aucun_appel.appels == []


def test_dates():
    assert str(lire_date("avant le 30/10/2026")) == "2026-10-30"
    assert str(lire_date("Date limite : 5 novembre 2026")) == "2026-11-05"
    assert str(lire_date("October 3, 2026")) == "2026-10-03"
    assert lire_date("dès que possible") is None
    assert expiree("01/01/2020") and not expiree("01/01/2099") and not expiree(None)


def test_ancienne_note_relue():
    ancienne = '{"score": 70, "verdict": "x", "points_forts": [], "ecarts": [], "entreprise": null, "intitule": "Dev", "langue": "fr", "lettre_demandee": false, "email_candidature": null, "date_limite": null, "consignes": null, "alerte": null}'
    n = lire_note(ancienne)
    assert n.score == 70 and n.exigences == [] and n.recommandation == "pari"


def test_doublon_entre_sites(tmp_path: Path):
    db = Base(tmp_path / "t.db")
    desc = "Missions : interfaces VueJS, API REST, encadrement. " * 20
    a = db.ajouter(Offre(source="novojob", ref="1", titre="Développeur Front-End", description=desc))
    assert db.doublon(Offre(source="educarriere", ref="9", titre="DEVELOPPEUR FRONT END", description=desc)) == a
    assert db.doublon(Offre(source="educarriere", ref="9", titre="Développeur Front-End", description="Autre chose " * 40)) is None
    assert db.doublon(Offre(source="novojob", ref="2", titre="Développeur Front-End", description=desc)) is None  # même site
    db.fermer()


def test_suivi_sans_dossier_et_relances(tmp_path: Path):
    from datetime import date, timedelta
    db = Base(tmp_path / "t.db")
    i = db.ajouter(Offre(source="manuel", ref="x", titre="Dev"))
    db.noter(i, note_test())
    assert db.changer_statut(i, "ignore")                    # pas besoin de dossier
    assert db.sans_dossier(0, 10) == []                       # une offre ignorée ne coûte plus rien
    assert db.changer_statut(i, "envoye")
    assert db.relances_dues(7) == []
    assert [r["id"] for r in db.relances_dues(7, date.today() + timedelta(days=8))] == [i]
    db.marquer_relance(i)
    assert db.relances_dues(7, date.today() + timedelta(days=8)) == []
    assert db.changer_statut(i, "nouveau") and db.suivi(i) is None
    db.fermer()


def test_offre_expiree_exclue(tmp_path: Path):
    db = Base(tmp_path / "t.db")
    i = db.ajouter(Offre(source="manuel", ref="old", titre="Dev"))
    db.noter(i, note_test(date_limite="01/01/2020"))
    assert db.sans_dossier(0, 10) == []
    assert db.classement(0, expirees=False) == [] and len(db.classement(0)) == 1
    db.fermer()


def test_web(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    from fastapi.testclient import TestClient
    from jobbot import config as conf, db as dbmod
    from jobbot.web import serveur

    base = tmp_path / "web.db"
    monkeypatch.setattr(dbmod.Base.__init__, "__defaults__", (base,))
    monkeypatch.setattr(render, "SORTIE", tmp_path / "candidatures")
    monkeypatch.setattr(serveur, "Claude", FauxClaude)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    serveur.app.state.jeton = "secret"
    c = TestClient(serveur.app)
    assert c.get("/").status_code == 401                      # sans jeton : refusé
    r = c.get("/?t=secret", follow_redirects=False)
    assert r.status_code == 303 and "jobbot=secret" in r.headers["set-cookie"]
    c.cookies.set("jobbot", "secret")
    assert "Rien à traiter" in c.get("/").text

    r = c.post("/coller", data={"texte": OFFRE_TEXTE, "lettre": "auto"}, headers={"Accept": "application/json"})
    assert r.status_code == 200
    tid = r.json()["id"]
    for _ in range(100):
        t = c.get(f"/api/taches/{tid}").json()
        if t["etat"] != "en_cours":
            break
        time.sleep(0.05)
    assert t["etat"] == "ok", t["lignes"]
    oid = int(t["lien"].rsplit("/", 1)[1])
    page = c.get(f"/offre/{oid}").text
    assert "Copier le message" in page and "Kubernetes" in page and "Combien d&#39;utilisateurs" in page
    assert c.get(f"/fichiers/{oid}/CV_Jean_Luc_Houedanou.pdf").status_code == 200
    assert c.get(f"/fichiers/{oid}/..%2F..%2Fjobbot.db").status_code == 404
    assert "Développeur Front-End Senior" in c.get("/").text
    r = c.post(f"/offre/{oid}/statut", data={"statut": "envoye"}, headers={"Accept": "application/json"})
    assert r.json()["ok"]
    assert "Envoyée" in c.get("/suivi").text
    assert "Relance" in c.get(f"/offre/{oid}").text
    r = c.post(f"/offre/{oid}/entretien", headers={"Accept": "application/json"})
    for _ in range(100):
        if c.get(f"/api/taches/{r.json()['id']}").json()["etat"] != "en_cours":
            break
        time.sleep(0.05)
    assert "Parlez d&#39;un projet VueJS" in c.get(f"/offre/{oid}").text

    # Documents du dossier : CV ATS en premier, téléchargements Markdown
    assert "CV pour logiciels de tri (ATS)" in page and "CV_ATS_Jean_Luc_Houedanou.md" in page
    assert c.get(f"/fichiers/{oid}/CV_ATS_Jean_Luc_Houedanou.pdf").status_code == 200

    # Nouvelle offre par son lien seul : la page est lue, puis le dossier est préparé
    monkeypatch.setattr(serveur.pipeline.lien, "Http", lambda: FauxPage(PAGE_OFFRE))
    assert "Lien de l'annonce" in c.get("/coller").text
    r = c.post("/coller", data={"url": "https://acme.ci/emploi/42"}, headers={"Accept": "application/json"})
    assert r.status_code == 200
    for _ in range(100):
        t = c.get(f"/api/taches/{r.json()['id']}").json()
        if t["etat"] != "en_cours":
            break
        time.sleep(0.05)
    assert t["etat"] == "ok" and t["lien"].startswith("/offre/"), t["lignes"]
    assert "Lettre de motivation" in c.get(t["lien"]).text            # lettre par défaut sur cette page
    r = c.post("/coller", data={"url": "https://www.linkedin.com/jobs/view/1"}, headers={"Accept": "application/json"})
    assert r.status_code == 422 and "colle-le" in r.json()["erreur"]
    assert c.post("/coller", data={}, headers={"Accept": "application/json"}).status_code == 422


def test_web_sans_cle(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    from fastapi.testclient import TestClient
    from jobbot import db as dbmod
    from jobbot.dates import date_publication
    from jobbot.web import serveur

    monkeypatch.setattr(dbmod.Base.__init__, "__defaults__", (tmp_path / "web.db",))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    db = Base()
    db.ajouter(Offre(source="novojob", ref="1", titre="Développeur Frontend Vue", lieu="Abidjan",
                     publie_le="Mon, 16 Nov 2026 21:31:46 +0100", description="React, Vue"))
    db.ajouter(Offre(source="novojob", ref="2", titre="Comptable", publie_le="Mon, 16 Nov 2026 10:00:00 +0100"),
               filtre_ok=False)
    db.fermer()
    assert str(date_publication("Mon, 16 Nov 2026 21:31:46 +0100")) == "2026-11-16"
    assert str(date_publication("", "2026-11-02T10:00:00")) == "2026-11-02"

    serveur.app.state.jeton = "secret"
    c = TestClient(serveur.app)
    c.cookies.set("jobbot", "secret")
    page = c.get("/?periode=tout").text                     # sans clé : vue « Non notées » par défaut
    assert "Offres collectées" in page and "Développeur Frontend Vue" in page and "Comptable" not in page
    assert "Collecter les offres" in page and "Mode sans clé API" in page
    assert "Comptable" in c.get("/?vue=a_noter&periode=tout&tout=1").text
    r = c.post("/lancer", data={"quoi": "go"}, headers={"Accept": "application/json"})
    assert r.status_code == 412 and "ANTHROPIC_API_KEY" in r.json()["erreur"]
    page1 = c.get("/offre/1").text
    assert "Pour la noter" in page1 and "/candidature 1" in page1

    # Sans clé : « Nouvelle offre » enregistre l'offre (aucune IA) et renvoie vers Claude Code
    page = c.get("/coller").text
    assert "Lire et enregistrer l'offre" in page and "Aucune IA" in page and "/candidature" in page
    r = c.post("/coller", data={"texte": OFFRE_TEXTE}, headers={"Accept": "application/json"})
    assert r.status_code == 200
    for _ in range(100):
        t = c.get(f"/api/taches/{r.json()['id']}").json()
        if t["etat"] != "en_cours":
            break
        time.sleep(0.05)
    assert t["etat"] == "ok" and t["lien"].startswith("/offre/"), t["lignes"]
    assert any("/candidature" in l for l in t["lignes"])
    assert "Offre pas encore notée" in c.get(t["lien"]).text


def test_importer_dossier_claude_code(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys):
    """Dossier rédigé dans Claude Code : aucune clé API, mêmes garde-fous."""
    import json

    from jobbot import importer
    from jobbot.__main__ import main

    monkeypatch.setattr(render, "SORTIE", tmp_path / "candidatures")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    rep = FauxClaude().demander("", "", "", "", _Reponse)
    entree = {"offre": None, "note": note_test().model_dump(), "cv": rep.cv.model_dump(),
              "lettre": rep.lettre.model_dump(), "message": rep.message.model_dump(), "a_completer": rep.a_completer}
    fichier = tmp_path / "offre-1.json"
    fichier.write_text(json.dumps(entree, ensure_ascii=False), encoding="utf-8")

    db = Base(tmp_path / "test.db")
    offre_id = pipeline.ajouter_a_la_main(db, OFFRE_TEXTE)
    oid, chemin, dossier = importer.importer(db, fichier, offre_id)
    assert oid == offre_id and db.note(offre_id).score == 88
    assert any("Kubernetes" in a for a in dossier.avertissements)       # compétence inventée signalée
    assert any("« 73 »" in a for a in dossier.avertissements)           # chiffre inventé signalé
    ats_md = (chemin / "CV_ATS_Jean_Luc_Houedanou.md").read_text(encoding="utf-8")
    assert "Kubernetes" not in ats_md and "WeDev Group" in ats_md
    assert (chemin / "Lettre_Jean_Luc_Houedanou.md").exists() and (chemin / "Email_Jean_Luc_Houedanou.md").exists()
    assert db.classement(80)[0]["statut"] == "a_relire"

    # Offre absente de la base : le bloc « offre » du fichier suffit
    entree["offre"] = {"titre": "Lead Front-End", "texte": OFFRE_TEXTE + " Autre annonce.", "url": "https://acme.ci/2"}
    fichier.write_text(json.dumps(entree, ensure_ascii=False), encoding="utf-8")
    oid2, _, _ = importer.importer(db, fichier)
    assert oid2 != offre_id and db.offre(oid2).titre == "Lead Front-End"
    db.fermer()

    # Fichier incomplet : message lisible, pas de trace Python
    entree.pop("message")
    fichier.write_text(json.dumps(entree, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(SystemExit) as err:
        importer.lire(fichier)
    assert "message" in str(err.value) and "python -m jobbot schema" in str(err.value)
    assert '"cv"' in importer.schema() and '"note"' in importer.schema()

    # Ligne de commande : schema et montrer fonctionnent sans clé
    from jobbot import db as dbmod
    monkeypatch.setattr(dbmod.Base.__init__, "__defaults__", (tmp_path / "test.db",))
    main(["montrer", str(offre_id)])
    sortie = capsys.readouterr().out
    assert f"Offre #{offre_id}" in sortie and "Banque XYZ" in sortie
