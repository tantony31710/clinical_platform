"""
core/db.py — Secure database access layer for the Clinical Platform.

Design principles:
  - Connection string loaded from DATABASE_URL environment variable only.
  - All queries use parameterized placeholders — no string interpolation.
  - DatabaseConnection context manager ensures connections are always closed.
  - Patient isolation: every query is scoped to the authenticated patient_id.
  - No debug output in production.
"""
import os
import json
import logging
from contextlib import contextmanager
from datetime import datetime, timezone

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ── Connection string ─────────────────────────────────────────────────────────
_DATABASE_URL: str | None = os.environ.get("DATABASE_URL")

if not _DATABASE_URL:
    logger.warning(
        "[DB] DATABASE_URL environment variable is not set. "
        "Database features will be unavailable."
    )


# ── Context manager ───────────────────────────────────────────────────────────
class DatabaseConnection:
    """Context manager that opens and closes a psycopg2 connection safely."""

    def __enter__(self):
        if not _DATABASE_URL:
            raise RuntimeError(
                "DATABASE_URL is not configured. "
                "Set it as an environment variable."
            )
        self.conn = psycopg2.connect(_DATABASE_URL, cursor_factory=RealDictCursor)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()
        return False  # Re-raise any exception


# ── Schema initialisation ─────────────────────────────────────────────────────
def init_db() -> None:
    """Create tables if they do not exist. Called once at app startup."""
    if not _DATABASE_URL:
        logger.warning("[DB] Skipping init_db — DATABASE_URL not set.")
        return

    ddl = """
    CREATE TABLE IF NOT EXISTS assessments (
        id          BIGSERIAL PRIMARY KEY,
        patient_id  TEXT        NOT NULL,
        profile     JSONB       NOT NULL,
        results     JSONB       NOT NULL,
        created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
    );

    CREATE INDEX IF NOT EXISTS idx_assessments_patient_id
        ON assessments (patient_id);
    """
    try:
        with DatabaseConnection() as conn:
            with conn.cursor() as cur:
                cur.execute(ddl)
        logger.info("[DB] Schema ready.")
    except Exception as exc:
        logger.error("[DB] init_db failed: %s", exc)
        raise


# ── Write ─────────────────────────────────────────────────────────────────────
def save_assessment(patient_id: str, profile: dict, results: dict) -> None:
    """
    Persist an assessment result for a patient.

    Args:
        patient_id: The authenticated user's ID (from session, never from request body).
        profile:    Sanitized input values that were assessed.
        results:    Diagnostic output from the engine.
    """
    if not _DATABASE_URL:
        logger.warning("[DB] save_assessment skipped — DATABASE_URL not set.")
        return

    sql = """
    INSERT INTO assessments (patient_id, profile, results, created_at)
    VALUES (%s, %s, %s, %s)
    """
    params = (
        patient_id,
        json.dumps(profile),
        json.dumps(results),
        datetime.now(timezone.utc),
    )
    with DatabaseConnection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)


# ── Read ──────────────────────────────────────────────────────────────────────
def get_patient_history(patient_id: str) -> list[dict]:
    """
    Fetch all past assessments for a patient, ordered oldest → newest.

    Args:
        patient_id: The authenticated user's ID. ALWAYS comes from the session,
                    never from user-controlled request parameters.

    Returns:
        List of dicts with keys: id, timestamp, profile, results.
    """
    if not _DATABASE_URL:
        return []

    sql = """
    SELECT id, created_at, profile, results
    FROM assessments
    WHERE patient_id = %s
    ORDER BY created_at ASC
    LIMIT 500
    """
    with DatabaseConnection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (patient_id,))
            rows = cur.fetchall()

    history = []
    for row in rows:
        history.append({
            "id":        row["id"],
            "timestamp": row["created_at"].isoformat() if row["created_at"] else None,
            "profile":   row["profile"] if isinstance(row["profile"], dict) else json.loads(row["profile"]),
            "results":   row["results"] if isinstance(row["results"], dict) else json.loads(row["results"]),
        })
    return history
