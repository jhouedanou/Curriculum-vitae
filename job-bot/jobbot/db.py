"""Base SQLite : offres vues, notes, dossiers préparés."""
from __future__ import annotations

import json
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import BASE
from .models import Note, Offre

SCHEMA = """
CREATE TABLE IF NOT EXISTS offres (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source      TEXT NOT NULL,
    ref         TEXT NOT NULL,
    titre       TEXT NOT NULL,
    url         TEXT,
    entreprise  TEXT,
    lieu        TEXT,
    publie_le   TEXT,
    description TEXT,
    filtre_ok   INTEGER DEFAULT 1,
    vue_le      TEXT NOT NULL,
    UNIQUE(source, ref)
);
CREATE TABLE IF NOT EXISTS notes (
    offre_id INTEGER PRIMARY KEY REFERENCES offres(id),
    score    INTEGER NOT NULL,
    detail   TEXT NOT NULL,
    note_le  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS dossiers (
    offre_id INTEGER PRIMARY KEY REFERENCES offres(id),
    chemin   TEXT NOT NULL,
    statut   TEXT NOT NULL DEFAULT 'a_relire',  -- a_relire, envoye, ignore
    cree_le  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS meta (
    cle    TEXT PRIMARY KEY,
    valeur TEXT
);
"""


def _maintenant() -> str:
    return datetime.now().isoformat(timespec="seconds")


class Base:
    def __init__(self, chemin: Path = BASE):
        self.cx = sqlite3.connect(chemin)
        self.cx.row_factory = sqlite3.Row
        self.cx.executescript(SCHEMA)

    # ── Offres ────────────────────────────────────────────
    def existe(self, source: str, ref: str) -> bool:
        r = self.cx.execute("SELECT 1 FROM offres WHERE source=? AND ref=?", (source, ref)).fetchone()
        return r is not None

    def ajouter(self, o: Offre, filtre_ok: bool = True) -> Optional[int]:
        """Ajoute l'offre si elle est nouvelle. Renvoie son numéro, ou None si déjà connue."""
        with self.cx:
            cur = self.cx.execute(
                """INSERT OR IGNORE INTO offres
                   (source, ref, titre, url, entreprise, lieu, publie_le, description, filtre_ok, vue_le)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (o.source, o.ref, o.titre, o.url, o.entreprise, o.lieu, o.publie_le,
                 o.description, int(filtre_ok), _maintenant()),
            )
        return cur.lastrowid if cur.rowcount else None

    def offre(self, offre_id: int) -> Optional[Offre]:
        r = self.cx.execute("SELECT * FROM offres WHERE id=?", (offre_id,)).fetchone()
        return _vers_offre(r) if r else None

    def a_noter(self, limite: int) -> list[Offre]:
        rows = self.cx.execute(
            """SELECT o.* FROM offres o LEFT JOIN notes n ON n.offre_id = o.id
               WHERE n.offre_id IS NULL AND o.filtre_ok = 1
               ORDER BY o.id DESC LIMIT ?""",
            (limite,),
        ).fetchall()
        return [_vers_offre(r) for r in rows]

    # ── Notes ─────────────────────────────────────────────
    def noter(self, offre_id: int, note: Note) -> None:
        with self.cx:
            self.cx.execute(
                "INSERT OR REPLACE INTO notes (offre_id, score, detail, note_le) VALUES (?,?,?,?)",
                (offre_id, note.score, note.model_dump_json(), _maintenant()),
            )

    def note(self, offre_id: int) -> Optional[Note]:
        r = self.cx.execute("SELECT detail FROM notes WHERE offre_id=?", (offre_id,)).fetchone()
        return Note.model_validate_json(r["detail"]) if r else None

    def classement(self, score_min: int = 0, limite: int = 30) -> list[sqlite3.Row]:
        return self.cx.execute(
            """SELECT o.id, o.source, o.titre, o.entreprise, o.url, n.score, n.detail,
                      d.statut, d.chemin
               FROM notes n JOIN offres o ON o.id = n.offre_id
               LEFT JOIN dossiers d ON d.offre_id = o.id
               WHERE n.score >= ?
               ORDER BY n.score DESC, o.id DESC LIMIT ?""",
            (score_min, limite),
        ).fetchall()

    def sans_dossier(self, score_min: int, limite: int) -> list[int]:
        rows = self.cx.execute(
            """SELECT n.offre_id FROM notes n LEFT JOIN dossiers d ON d.offre_id = n.offre_id
               WHERE d.offre_id IS NULL AND n.score >= ?
               ORDER BY n.score DESC LIMIT ?""",
            (score_min, limite),
        ).fetchall()
        return [r["offre_id"] for r in rows]

    # ── Dossiers ──────────────────────────────────────────
    def enregistrer_dossier(self, offre_id: int, chemin: Path) -> None:
        with self.cx:
            self.cx.execute(
                "INSERT OR REPLACE INTO dossiers (offre_id, chemin, statut, cree_le) VALUES (?,?, 'a_relire', ?)",
                (offre_id, str(chemin), _maintenant()),
            )

    def changer_statut(self, offre_id: int, statut: str) -> bool:
        with self.cx:
            cur = self.cx.execute("UPDATE dossiers SET statut=? WHERE offre_id=?", (statut, offre_id))
        return cur.rowcount > 0

    # ── Méta (ex. : dernière visite d'une source) ─────────
    def derniere_visite(self, source: str) -> float:
        r = self.cx.execute("SELECT valeur FROM meta WHERE cle=?", (f"visite:{source}",)).fetchone()
        return float(r["valeur"]) if r else 0.0

    def marquer_visite(self, source: str) -> None:
        with self.cx:
            self.cx.execute(
                "INSERT OR REPLACE INTO meta (cle, valeur) VALUES (?,?)",
                (f"visite:{source}", str(time.time())),
            )

    def fermer(self) -> None:
        self.cx.close()


def _vers_offre(r: sqlite3.Row) -> Offre:
    return Offre(
        id=r["id"], source=r["source"], ref=r["ref"], titre=r["titre"], url=r["url"] or "",
        entreprise=r["entreprise"] or "", lieu=r["lieu"] or "", publie_le=r["publie_le"] or "",
        description=r["description"] or "",
    )


def detail_note(row: sqlite3.Row) -> dict:
    return json.loads(row["detail"])
