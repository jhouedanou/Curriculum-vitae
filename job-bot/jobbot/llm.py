"""Appels à Claude avec sortie JSON garantie (structured outputs)."""
from __future__ import annotations

import os
from typing import Protocol, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLM(Protocol):
    def demander(self, modele: str, systeme: str, cv: str, consigne: str, format: type[T],
                 max_tokens: int = 4000) -> T: ...


class Claude:
    def __init__(self) -> None:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise SystemExit(
                "Clé API manquante. Crée un fichier .env avec ANTHROPIC_API_KEY=sk-ant-…\n"
                "(clé à créer sur https://platform.claude.com)"
            )
        import anthropic

        self.client = anthropic.Anthropic()

    def demander(self, modele, systeme, cv, consigne, format, max_tokens=4000):
        rep = self.client.messages.parse(
            model=modele,
            max_tokens=max_tokens,
            # Le CV est identique à chaque appel : on le met en cache (moins cher, plus rapide).
            system=[
                {"type": "text", "text": systeme},
                {"type": "text", "text": f"<cv>\n{cv}\n</cv>", "cache_control": {"type": "ephemeral"}},
            ],
            messages=[{"role": "user", "content": consigne}],
            output_format=format,
        )
        if rep.stop_reason == "max_tokens":
            raise RuntimeError("Réponse coupée (max_tokens). Relance ou augmente max_tokens.")
        if rep.parsed_output is None:
            raise RuntimeError(f"Pas de réponse exploitable (stop_reason={rep.stop_reason}).")
        return rep.parsed_output


def charger_env() -> None:
    """Lit le fichier .env du projet (format CLE=valeur), sans dépendance externe."""
    from .config import RACINE

    fichier = RACINE / ".env"
    if not fichier.exists():
        return
    for ligne in fichier.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if ligne and not ligne.startswith("#") and "=" in ligne:
            cle, val = ligne.split("=", 1)
            os.environ.setdefault(cle.strip(), val.strip().strip('"').strip("'"))
