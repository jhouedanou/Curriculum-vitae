"""Tests sans Internet ni clé API : python -m pytest -q"""
from __future__ import annotations

from pathlib import Path

import pytest

from jobbot import pipeline, render
from jobbot.db import Base
from jobbot.models import CVAdapte, ExperienceAdaptee, Lettre, Message, Note, Offre
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


class FauxClaude:
    """Remplace Claude dans les tests : réponses fixes, avec des erreurs volontaires."""

    def demander(self, modele, systeme, cv, consigne, format, max_tokens=4000):
        if format is Note:
            return Note(score=88, verdict="Très bon profil.", points_forts=["VueJS expert"], ecarts=["Secteur bancaire"],
                        entreprise="Banque XYZ", intitule="Développeur Front-End Senior", langue="fr",
                        lettre_demandee=True, email_candidature="recrutement@xyz.ci", date_limite="30/10/2026",
                        consignes="CV + lettre", alerte=None)
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
    assert [o.ref for o in offres] == ["156700", "156701"]
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
    assert pipeline.collecter(db, FauxHttp()) == 3      # 1 Novojob + 1 Educarrière + 1 Remotive
    assert pipeline.collecter(db, FauxHttp()) == 0      # rien de nouveau au 2e passage
    a_noter = db.a_noter(10)
    assert len(a_noter) == 3
    edu = next(o for o in a_noter if o.source == "educarriere")
    assert "VueJS" in edu.description                    # page de détail lue
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
    db.fermer()
