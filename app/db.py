"""SQLite database setup with FTS5 for scheme search."""

import sqlite3
import json
import os
from app.config import settings
from app.models import SchemeRecord


def get_db_path() -> str:
    return settings.database_path


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Create tables and FTS5 virtual table."""
    conn = get_connection()
    cur = conn.cursor()

    # Main schemes table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS schemes (
            id TEXT PRIMARY KEY,
            name_en TEXT NOT NULL,
            name_hi TEXT NOT NULL,
            name_ta TEXT NOT NULL,
            category TEXT NOT NULL,
            description_en TEXT,
            description_hi TEXT,
            description_ta TEXT,
            eligibility_json TEXT,
            eligibility_summary_en TEXT,
            eligibility_summary_hi TEXT,
            eligibility_summary_ta TEXT,
            documents_en TEXT,
            documents_hi TEXT,
            documents_ta TEXT,
            benefits_en TEXT,
            benefits_hi TEXT,
            benefits_ta TEXT,
            official_url TEXT,
            source TEXT
        )
    """)

    # FTS5 virtual table for keyword search
    cur.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS schemes_fts USING fts5(
            id,
            name_en,
            name_hi,
            category,
            description_en,
            eligibility_summary_en,
            benefits_en,
            content='schemes',
            content_rowid='rowid'
        )
    """)

    conn.commit()
    conn.close()


def insert_scheme(scheme: SchemeRecord):
    """Insert or replace a scheme record."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT OR REPLACE INTO schemes (
            id, name_en, name_hi, name_ta, category,
            description_en, description_hi, description_ta,
            eligibility_json,
            eligibility_summary_en, eligibility_summary_hi, eligibility_summary_ta,
            documents_en, documents_hi, documents_ta,
            benefits_en, benefits_hi, benefits_ta,
            official_url, source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        scheme.id, scheme.name_en, scheme.name_hi, scheme.name_ta, scheme.category,
        scheme.description_en, scheme.description_hi, scheme.description_ta,
        scheme.eligibility.model_dump_json(),
        scheme.eligibility_summary_en, scheme.eligibility_summary_hi, scheme.eligibility_summary_ta,
        json.dumps(scheme.documents_en), json.dumps(scheme.documents_hi), json.dumps(scheme.documents_ta),
        scheme.benefits_en, scheme.benefits_hi, scheme.benefits_ta,
        scheme.official_url, scheme.source,
    ))

    # Update FTS index
    cur.execute("""
        INSERT OR REPLACE INTO schemes_fts (
            id, name_en, name_hi, category,
            description_en, eligibility_summary_en, benefits_en
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        scheme.id, scheme.name_en, scheme.name_hi, scheme.category,
        scheme.description_en, scheme.eligibility_summary_en, scheme.benefits_en,
    ))

    conn.commit()
    conn.close()


def get_all_schemes() -> list[dict]:
    """Get all scheme records."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM schemes").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def search_schemes_fts(query: str) -> list[dict]:
    """Full-text search on schemes."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id FROM schemes_fts WHERE schemes_fts MATCH ? ORDER BY rank LIMIT 5",
            (query,)
        ).fetchall()
        ids = [row["id"] for row in rows]
        if not ids:
            return []
        placeholders = ",".join("?" * len(ids))
        schemes = conn.execute(
            f"SELECT * FROM schemes WHERE id IN ({placeholders})", ids
        ).fetchall()
        return [dict(s) for s in schemes]
    except Exception:
        return []
    finally:
        conn.close()


def row_to_scheme(row: dict) -> SchemeRecord:
    """Convert a DB row dict back to a SchemeRecord."""
    from app.models import SchemeEligibility
    return SchemeRecord(
        id=row["id"],
        name_en=row["name_en"],
        name_hi=row["name_hi"],
        name_ta=row["name_ta"],
        category=row["category"],
        description_en=row["description_en"],
        description_hi=row["description_hi"],
        description_ta=row["description_ta"],
        eligibility=SchemeEligibility.model_validate_json(row["eligibility_json"]),
        eligibility_summary_en=row["eligibility_summary_en"],
        eligibility_summary_hi=row["eligibility_summary_hi"],
        eligibility_summary_ta=row["eligibility_summary_ta"],
        documents_en=json.loads(row["documents_en"]),
        documents_hi=json.loads(row["documents_hi"]),
        documents_ta=json.loads(row["documents_ta"]),
        benefits_en=row["benefits_en"],
        benefits_hi=row["benefits_hi"],
        benefits_ta=row["benefits_ta"],
        official_url=row["official_url"],
        source=row["source"],
    )
