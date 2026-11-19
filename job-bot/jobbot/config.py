"""Chargement de config.yaml et cv.yaml."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml

# Dossier du projet (celui qui contient cv.yaml). Modifiable avec JOBBOT_HOME.
RACINE = Path(os.environ.get("JOBBOT_HOME", Path(__file__).resolve().parent.parent))
SORTIE = RACINE / "candidatures"
BASE = RACINE / "jobbot.db"


def _lire_yaml(nom: str) -> dict:
    chemin = RACINE / nom
    if not chemin.exists():
        raise SystemExit(f"Fichier introuvable : {chemin}")
    with chemin.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@lru_cache
def config() -> dict:
    return _lire_yaml("config.yaml")


def _fichier_cv(langue: str) -> str:
    """cv_en.yaml pour les offres en anglais (s'il existe), sinon cv.yaml."""
    if langue == "en" and (RACINE / "cv_en.yaml").exists():
        return "cv_en.yaml"
    return "cv.yaml"


@lru_cache
def cv(langue: str = "fr") -> dict:
    return _lire_yaml(_fichier_cv(langue))


def cv_texte(langue: str = "fr") -> str:
    """Le CV en YAML brut : c'est ce que Claude lit."""
    return (RACINE / _fichier_cv(langue)).read_text(encoding="utf-8")
