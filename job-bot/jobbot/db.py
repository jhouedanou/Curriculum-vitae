"""Base SQLite : offres vues, notes, dossiers préparés, suivi des candidatures."""
from __future__ import annotations

import difflib
import json
import re
import sqlite3
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

from .config import BASE
from .dates import expiree
from .models import Note, Offre, lire_note
from .sources.base import normaliser

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
    statut   TEXT NOT NULL DEFAULT 'a_relire',  -- ancien suivi, remplacé par la table suivi
    cree_le  TEXT NOT NULL
);
-- Suivi d'une offre, avec ou sans dossier
CREATE TABLE IF NOT EXISTS suivi (
    offre_id   INTEGER PRIMARY KEY REFERENCES offres(id),
    statut     TEXT NOT NULL,          -- a_relire, envoye, entretien, refus, ignore
    maj_le     TEXT NOT NULL,
    envoye_le  TEXT,
    relance_le TEXT,
    remarque   TEXT
);
-- Textes générés en plus du dossier (préparation d'entretien, relance)
CREATE TABLE IF NOT EXISTS extras (
    offre_id INTEGER NOT NULL REFERENCES offres(id),
    type     TEXT NOT NULL,
    contenu  TEXT NOT NULL,
    cree_le  TEXT NOT NULL,
    PRIMARY KEY (offre_id, type)
);
CREATE TABLE IF NOT EXISTS meta (
    cle    TEXT PRIMARY KEY,
    valeur TEXT
);
"""

STATUTS = {
    "a_relire": "À relire",
    "envoye": "Envoyée",
    "entretien": "Entretien",
    "refus": "Refus",
    "ignore": "Ignorée",
}


def _maintenant() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _cle_titre(titre: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", normaliser(titre)).strip()


class Base:
    def __init__(self, chemin: Path = BASE):
        # check_same_thread=False : l'interface web et ses tâches de fond partagent la base.
        self.cx = sqlite3.connect(chemin, timeout=30, check_same_thread=False)
        self.cx.row_factory = sqlite3.Row
        self.cx.execute("PRAGMA journal_mode=WAL")
        self.cx.executescript(SCHEMA)
        self._migrer()

    def _migrer(self) -> None:
        cols = {r["name"] for r in self.cx.execute("PRAGMA table_info(offres)")}
        with self.cx:
            if "doublon_de" not in cols:
                self.cx.execute("ALTER TABLE offres ADD COLUMN doublon_de INTEGER")
            # Les anciens statuts (table dossiers) passent dans la table suivi.
            self.cx.execute(
                """INSERT OR IGNORE INTO suivi (offre_id, statut, maj_le, envoye_le)
                   SELECT offre_id, statut, cree_le, CASE WHEN statut='envoye' THEN cree_le END FROM dossiers"""
            )

    # ── Offres ────────────────────────────────────────────
    def existe(self, source: str, ref: str) -> bool:
        r = self.cx.execute("SELECT 1 FROM offres WHERE source=? AND ref=?", (source, ref)).fetchone()
        return r is not None

    def ajouter(self, o: Offre, filtre_ok: bool = True, doublon_de: Optional[int] = None) -> Optional[int]:
        """Ajoute l'offre si elle est nouvelle. Renvoie son numéro, ou None si déjà connue."""
        with self.cx:
            cur = self.cx.execute(
                """INSERT OR IGNORE INTO offres
                   (source, ref, titre, url, entreprise, lieu, publie_le, description, filtre_ok, vue_le, doublon_de)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (o.source, o.ref, o.titre, o.url, o.entreprise, o.lieu, o.publie_le,
                 o.description, int(filtre_ok), _maintenant(), doublon_de),
            )
        return cur.lastrowid if cur.rowcount else None

    def doublon(self, o: Offre, jours: int = 45) -> Optional[int]:
        """Même offre déjà vue sur un autre site ? Renvoie son numéro."""
        cle = _cle_titre(o.titre)
        if len(cle) < 6:
            return None
        depuis = (datetime.now() - timedelta(days=jours)).isoformat(timespec="seconds")
        rows = self.cx.execute(
            """SELECT id, titre, entreprise, description FROM offres
               WHERE source != ? AND vue_le >= ? AND doublon_de IS NULL""",
            (o.source, depuis),
        ).fetchall()
        ent = normaliser(o.entreprise).strip()
        desc = normaliser(o.description)[:2000]
        for r in rows:
            if _cle_titre(r["titre"]) != cle:
                continue
            autre_ent = normaliser(r["entreprise"] or "").strip()
            if ent and autre_ent:
                if ent == autre_ent:
                    return r["id"]
                continue
            autre_desc = normaliser(r["description"] or "")[:2000]
            if desc and autre_desc and difflib.SequenceMatcher(None, desc, autre_desc).quick_ratio() >= 0.75 \
                    and difflib.SequenceMatcher(None, desc, autre_desc).ratio() >= 0.6:
                return r["id"]
        return None

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

    def nb_a_noter(self) -> int:
        return self.cx.execute(
            """SELECT COUNT(*) FROM offres o LEFT JOIN notes n ON n.offre_id = o.id
               WHERE n.offre_id IS NULL AND o.filtre_ok = 1"""
        ).fetchone()[0]

    # ── Notes ─────────────────────────────────────────────
    def noter(self, offre_id: int, note: Note) -> None:
        with self.cx:
            self.cx.execute(
                "INSERT OR REPLACE INTO notes (offre_id, score, detail, note_le) VALUES (?,?,?,?)",
                (offre_id, note.score, note.model_dump_json(), _maintenant()),
            )

    def note(self, offre_id: int) -> Optional[Note]:
        r = self.cx.execute("SELECT detail FROM notes WHERE offre_id=?", (offre_id,)).fetchone()
        return lire_note(r["detail"]) if r else None

    def classement(self, score_min: int = 0, limite: int = 30, *, expirees: bool = True,
                   statuts: Optional[list[str]] = None) -> list[sqlite3.Row]:
        """Offres notées, meilleures d'abord.

        expirees=False retire les offres dont la date limite est passée.
        statuts filtre sur le suivi (« nouveau » = pas encore suivie).
        """
        sql = """SELECT o.id, o.source, o.titre, o.entreprise, o.lieu, o.url, o.vue_le, n.score, n.detail,
                        s.statut, s.envoye_le, s.relance_le, d.chemin
                 FROM notes n JOIN offres o ON o.id = n.offre_id
                 LEFT JOIN dossiers d ON d.offre_id = o.id
                 LEFT JOIN suivi s ON s.offre_id = o.id
                 WHERE n.score >= ?"""
        args: list = [score_min]
        if statuts:
            conds = []
            if "nouveau" in statuts:
                conds.append("s.statut IS NULL")
            autres = [s for s in statuts if s != "nouveau"]
            if autres:
                conds.append(f"s.statut IN ({','.join('?' * len(autres))})")
                args += autres
            sql += f" AND ({' OR '.join(conds)})"
        sql += " ORDER BY n.score DESC, o.id DESC"
        rows = self.cx.execute(sql, args).fetchall()
        if not expirees:
            rows = [r for r in rows if not expiree(json.loads(r["detail"]).get("date_limite"))]
        return rows[:limite]

    def sans_dossier(self, score_min: int, limite: int) -> list[int]:
        """Meilleures offres sans dossier, ni expirées, ni écartées."""
        rows = self.cx.execute(
            """SELECT n.offre_id, n.detail FROM notes n
               LEFT JOIN dossiers d ON d.offre_id = n.offre_id
               LEFT JOIN suivi s ON s.offre_id = n.offre_id
               WHERE d.offre_id IS NULL AND n.score >= ? AND (s.statut IS NULL OR s.statut != 'ignore')
               ORDER BY n.score DESC""",
            (score_min,),
        ).fetchall()
        ids = [r["offre_id"] for r in rows if not expiree(json.loads(r["detail"]).get("date_limite"))]
        return ids[:limite]

    # ── Dossiers ──────────────────────────────────────────
    def enregistrer_dossier(self, offre_id: int, chemin: Path) -> None:
        with self.cx:
            self.cx.execute(
                "INSERT OR REPLACE INTO dossiers (offre_id, chemin, statut, cree_le) VALUES (?,?, 'a_relire', ?)",
                (offre_id, str(chemin), _maintenant()),
            )
            # Un nouveau dossier se relit, sauf si la candidature est déjà partie.
            self.cx.execute(
                """INSERT INTO suivi (offre_id, statut, maj_le) VALUES (?, 'a_relire', ?)
                   ON CONFLICT(offre_id) DO UPDATE SET statut='a_relire', maj_le=excluded.maj_le
                   WHERE suivi.statut IN ('ignore')""",
                (offre_id, _maintenant()),
            )

    def dossier(self, offre_id: int) -> Optional[Path]:
        r = self.cx.execute("SELECT chemin FROM dossiers WHERE offre_id=?", (offre_id,)).fetchone()
        return Path(r["chemin"]) if r else None

    # ── Suivi ─────────────────────────────────────────────
    def changer_statut(self, offre_id: int, statut: str) -> bool:
        """Change le suivi d'une offre (avec ou sans dossier). « nouveau » efface le suivi."""
        if not self.offre(offre_id):
            return False
        with self.cx:
            if statut == "nouveau":
                self.cx.execute("DELETE FROM suivi WHERE offre_id=?", (offre_id,))
                return True
            if statut not in STATUTS:
                raise ValueError(f"Statut inconnu : {statut}")
            maintenant = _maintenant()
            self.cx.execute(
                """INSERT INTO suivi (offre_id, statut, maj_le, envoye_le) VALUES (?,?,?,?)
                   ON CONFLICT(offre_id) DO UPDATE SET statut=excluded.statut, maj_le=excluded.maj_le,
                       envoye_le=COALESCE(suivi.envoye_le, excluded.envoye_le)""",
                (offre_id, statut, maintenant, maintenant if statut == "envoye" else None),
            )
            self.cx.execute("UPDATE dossiers SET statut=? WHERE offre_id=?", (statut, offre_id))
        return True

    def suivi(self, offre_id: int) -> Optional[sqlite3.Row]:
        return self.cx.execute("SELECT * FROM suivi WHERE offre_id=?", (offre_id,)).fetchone()

    def marquer_relance(self, offre_id: int) -> None:
        with self.cx:
            self.cx.execute("UPDATE suivi SET relance_le=? WHERE offre_id=?", (_maintenant(), offre_id))

    def relances_dues(self, apres_jours: int, aujourdhui: Optional[date] = None) -> list[sqlite3.Row]:
        """Candidatures envoyées depuis au moins N jours, pas encore relancées."""
        limite = datetime.combine(aujourdhui or date.today(), datetime.min.time()) - timedelta(days=apres_jours)
        return self.cx.execute(
            """SELECT o.id, o.titre, o.entreprise, s.envoye_le, n.detail FROM suivi s
               JOIN offres o ON o.id = s.offre_id LEFT JOIN notes n ON n.offre_id = o.id
               WHERE s.statut = 'envoye' AND s.relance_le IS NULL AND s.envoye_le <= ?
               ORDER BY s.envoye_le""",
            (limite.isoformat(timespec="seconds"),),
        ).fetchall()

    def compter_statuts(self) -> dict[str, int]:
        rows = self.cx.execute("SELECT statut, COUNT(*) c FROM suivi GROUP BY statut").fetchall()
        return {r["statut"]: r["c"] for r in rows}

    # ── Extras (entretien, relance) ───────────────────────
    def enregistrer_extra(self, offre_id: int, type_: str, contenu: str) -> None:
        with self.cx:
            self.cx.execute(
                "INSERT OR REPLACE INTO extras (offre_id, type, contenu, cree_le) VALUES (?,?,?,?)",
                (offre_id, type_, contenu, _maintenant()),
            )

    def extra(self, offre_id: int, type_: str) -> Optional[str]:
        r = self.cx.execute("SELECT contenu FROM extras WHERE offre_id=? AND type=?", (offre_id, type_)).fetchone()
        return r["contenu"] if r else None

    # ── Méta (ex. : dernière visite d'une source) ─────────
    def derniere_visite(self, source: str) -> float:
        r = self.cx.execute("SELECT valeur FROM meta WHERE cle=?", (f"visite:{source}",)).fetchone()
        return float(r["valeur"]) if r else 0.0

    def marquer_visite(self, source: str) -> None:
        self.ecrire_meta(f"visite:{source}", str(time.time()))

    def lire_meta(self, cle: str) -> Optional[str]:
        r = self.cx.execute("SELECT valeur FROM meta WHERE cle=?", (cle,)).fetchone()
        return r["valeur"] if r else None

    def ecrire_meta(self, cle: str, valeur: str) -> None:
        with self.cx:
            self.cx.execute("INSERT OR REPLACE INTO meta (cle, valeur) VALUES (?,?)", (cle, valeur))

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
