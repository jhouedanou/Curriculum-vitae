"""Importer un dossier rédigé dans Claude Code (sans clé API).

Claude Code lit l'offre et le CV, écrit un fichier JSON, puis lance :
    python -m jobbot importer dossier.json --offre 12
Le bot fait le reste sans IA : garde-fous, mise en page, PDF, suivi.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, ValidationError

from . import pipeline, render, writer
from .db import Base
from .models import CVAdapte, Dossier, Lettre, Message, Note


class OffreEntree(BaseModel):
    """À remplir seulement si l'offre n'est pas encore dans la base (pas de --offre)."""
    titre: str
    texte: str = Field(description="Texte complet de l'annonce")
    url: str = ""


class Entree(BaseModel):
    """Le fichier JSON attendu par « python -m jobbot importer »."""
    offre: Optional[OffreEntree] = Field(default=None, description="null si l'offre est déjà en base (--offre N)")
    note: Note
    cv: CVAdapte
    lettre: Optional[Lettre] = Field(default=None, description="null pour un dossier sans lettre")
    message: Message
    a_completer: list[str] = Field(default_factory=list,
                                   description="Questions au candidat : résultats non chiffrés dans le CV")


def schema() -> str:
    """Le format du fichier, pour celui qui le rédige."""
    return json.dumps(Entree.model_json_schema(), ensure_ascii=False, indent=2)


def lire(chemin: Path) -> Entree:
    try:
        return Entree.model_validate_json(Path(chemin).read_text(encoding="utf-8"))
    except ValidationError as err:
        lignes = [f"- {' → '.join(str(x) for x in e['loc'])} : {e['msg']}" for e in err.errors()]
        raise SystemExit("Le fichier ne suit pas le format attendu (python -m jobbot schema) :\n" + "\n".join(lignes))


def importer(db: Base, chemin: Path, offre_id: Optional[int] = None) -> tuple[int, Path, Dossier]:
    """Enregistre la note, applique les garde-fous, met en page. Renvoie (n° d'offre, dossier, dossier vérifié)."""
    e = lire(chemin)
    if offre_id is None:
        if not e.offre:
            raise SystemExit("Indique l'offre : --offre N, ou un bloc « offre » (titre, texte, url) dans le fichier.")
        if len(e.offre.texte.strip()) < 100:
            raise SystemExit("offre.texte est trop court : mets le texte complet de l'annonce.")
        offre_id = pipeline.ajouter_a_la_main(db, e.offre.texte, e.offre.url, e.offre.titre)
    o = db.offre(offre_id)
    if not o:
        raise SystemExit(f"Offre #{offre_id} inconnue.")
    db.noter(offre_id, e.note)
    dossier = writer.verifier(Dossier(cv=e.cv, lettre=e.lettre, message=e.message, a_completer=e.a_completer),
                              e.note.langue)
    chemin_dossier = render.generer(o, e.note, dossier)
    db.enregistrer_dossier(offre_id, chemin_dossier)
    return offre_id, chemin_dossier, dossier
