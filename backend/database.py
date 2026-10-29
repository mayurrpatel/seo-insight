"""
SQLite Database module for persisting SEO audit reports and history.
Zero-configuration, lightweight, and durable storage.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from typing import Optional
from urllib.parse import urlparse

DB_PATH = Path(__file__).parent / "seo_insight.db"
SAMPLE_JSON_PATH = Path(__file__).parent / "sample_data" / "sample_audit.json"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables and indexes."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audits (
                id TEXT PRIMARY KEY,
                target_url TEXT NOT NULL,
                domain TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                pages_scanned INTEGER NOT NULL DEFAULT 0,
                pages_discovered INTEGER NOT NULL DEFAULT 0,
                pages_failed INTEGER NOT NULL DEFAULT 0,
                health_score INTEGER NOT NULL DEFAULT 0,
                health_rating TEXT NOT NULL,
                critical_count INTEGER NOT NULL DEFAULT 0,
                high_count INTEGER NOT NULL DEFAULT 0,
                medium_count INTEGER NOT NULL DEFAULT 0,
                low_count INTEGER NOT NULL DEFAULT 0,
                total_issues INTEGER NOT NULL DEFAULT 0,
                robots_txt_found BOOLEAN NOT NULL DEFAULT 0,
                sitemap_found BOOLEAN NOT NULL DEFAULT 0,
                is_sample BOOLEAN NOT NULL DEFAULT 0,
                result_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audits_created_at ON audits(created_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audits_domain ON audits(domain)")
        conn.commit()

    # Seed sample audit if table is empty
    seed_sample_if_empty()


def seed_sample_if_empty():
    """Seed initial illustrative audit so history is never blank on fresh install."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS cnt FROM audits")
        row = cursor.fetchone()
        if row and row["cnt"] > 0:
            return

    if SAMPLE_JSON_PATH.exists():
        try:
            with open(SAMPLE_JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            save_audit(data)
        except Exception:
            pass


def save_audit(audit_data: dict) -> None:
    """Save or update an audit report into the database."""
    audit_id = audit_data.get("audit_id") or str(audit_data.get("id"))
    target_url = audit_data.get("target_url", "")
    parsed = urlparse(target_url)
    domain = parsed.netloc or parsed.path or "unknown"

    health = audit_data.get("health_score", {})
    score = health.get("score", 0)
    rating = health.get("rating", "N/A")
    crit = health.get("critical_count", 0)
    high = health.get("high_count", 0)
    med = health.get("medium_count", 0)
    low = health.get("low_count", 0)
    total_issues = health.get("total_issues", len(audit_data.get("issues", [])))

    created_at = audit_data.get("created_at") or datetime.now(timezone.utc).isoformat()
    timestamp = audit_data.get("timestamp") or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO audits (
                id, target_url, domain, timestamp, pages_scanned, pages_discovered,
                pages_failed, health_score, health_rating, critical_count, high_count,
                medium_count, low_count, total_issues, robots_txt_found, sitemap_found,
                is_sample, result_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            audit_id,
            target_url,
            domain,
            timestamp,
            audit_data.get("pages_scanned", 0),
            audit_data.get("pages_discovered", 0),
            audit_data.get("pages_failed", 0),
            score,
            rating,
            crit,
            high,
            med,
            low,
            total_issues,
            1 if audit_data.get("robots_txt_found") else 0,
            1 if audit_data.get("sitemap_found") else 0,
            1 if audit_data.get("is_sample") else 0,
            json.dumps(audit_data),
            created_at
        ))
        conn.commit()


def get_audit_by_id(audit_id: str) -> Optional[dict]:
    """Retrieve full audit JSON by its ID from the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT result_json FROM audits WHERE id = ?", (audit_id,))
        row = cursor.fetchone()
        if row and row["result_json"]:
            return json.loads(row["result_json"])
    return None


def get_audit_history() -> list[dict]:
    """Retrieve summarized history list of all previously audited reports."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                id, target_url, domain, timestamp, pages_scanned, pages_discovered,
                pages_failed, health_score, health_rating, critical_count, high_count,
                medium_count, low_count, total_issues, robots_txt_found, sitemap_found,
                is_sample, created_at
            FROM audits
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def delete_audit_by_id(audit_id: str) -> bool:
    """Delete an audit record from the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM audits WHERE id = ?", (audit_id,))
        conn.commit()
        return cursor.rowcount > 0
