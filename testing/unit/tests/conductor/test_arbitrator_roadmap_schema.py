"""Roadmap + body tables were added to the conductor schema.

These tests go straight at the backend (no Arbitrator facade yet — that
comes in a later commit). Goal: prove the schema additions load cleanly,
respect FKs, and accept sensible rows.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@pytest.fixture
def sqlite_conn(tmp_path):
    """Raw sqlite3 connection to a fresh DB loaded with the conductor schema."""
    import sqlite3
    from pathlib import Path

    schema_path = (
        Path(__file__).resolve().parents[4]
        / "plugins" / "dev-team" / "services" / "conductor"
        / "arbitrator" / "backends" / "schema.sql"
    )
    db = tmp_path / "test.db"
    conn = sqlite3.connect(db)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(schema_path.read_text())
    conn.commit()
    yield conn
    conn.close()


def test_roadmap_table_exists(sqlite_conn):
    row = sqlite_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='roadmap'"
    ).fetchone()
    assert row is not None


def test_plan_node_and_dependency_and_state_event_tables_exist(sqlite_conn):
    names = {
        r[0] for r in sqlite_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    assert {"plan_node", "node_dependency", "node_state_event"} <= names


def test_body_side_table_exists(sqlite_conn):
    row = sqlite_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='body'"
    ).fetchone()
    assert row is not None


def test_roadmap_insert_and_read(sqlite_conn):
    now = _now()
    sqlite_conn.execute(
        "INSERT INTO roadmap (roadmap_id, title, creation_date, modification_date) "
        "VALUES (?, ?, ?, ?)",
        ("rm-1", "Sample", now, now),
    )
    sqlite_conn.commit()
    row = sqlite_conn.execute(
        "SELECT title FROM roadmap WHERE roadmap_id='rm-1'"
    ).fetchone()
    assert row[0] == "Sample"


def test_plan_node_parent_fk_enforced(sqlite_conn):
    import sqlite3
    now = _now()
    sqlite_conn.execute(
        "INSERT INTO roadmap (roadmap_id, title, creation_date, modification_date) "
        "VALUES ('rm', 't', ?, ?)", (now, now),
    )
    sqlite_conn.commit()
    with pytest.raises(sqlite3.IntegrityError):
        # parent_id points at nonexistent node
        sqlite_conn.execute(
            "INSERT INTO plan_node (node_id, roadmap_id, parent_id, position, "
            "node_kind, title, creation_date, modification_date) "
            "VALUES ('child', 'rm', 'nonexistent', 1.0, 'compound', 'c', ?, ?)",
            (now, now),
        )


def test_node_dependency_unique_constraint(sqlite_conn):
    import sqlite3
    now = _now()
    sqlite_conn.execute(
        "INSERT INTO roadmap (roadmap_id, title, creation_date, modification_date) "
        "VALUES ('rm', 't', ?, ?)", (now, now),
    )
    for i in (1, 2):
        sqlite_conn.execute(
            "INSERT INTO plan_node (node_id, roadmap_id, position, node_kind, "
            "title, creation_date, modification_date) "
            "VALUES (?, 'rm', ?, 'compound', ?, ?, ?)",
            (f"n{i}", float(i), f"N{i}", now, now),
        )
    sqlite_conn.execute(
        "INSERT INTO node_dependency (node_id, depends_on_id, creation_date) "
        "VALUES ('n1', 'n2', ?)", (now,),
    )
    sqlite_conn.commit()
    with pytest.raises(sqlite3.IntegrityError):
        sqlite_conn.execute(
            "INSERT INTO node_dependency (node_id, depends_on_id, creation_date) "
            "VALUES ('n1', 'n2', ?)", (now,),
        )


def test_body_composite_primary_key(sqlite_conn):
    import sqlite3
    now = _now()
    sqlite_conn.execute(
        "INSERT INTO body (owner_type, owner_id, body_format, body_text, modification_date) "
        "VALUES ('plan_node', 'x', 'markdown', 'hello', ?)", (now,),
    )
    sqlite_conn.commit()
    # Same owner_type/owner_id → duplicate primary key.
    with pytest.raises(sqlite3.IntegrityError):
        sqlite_conn.execute(
            "INSERT INTO body (owner_type, owner_id, body_format, body_text, modification_date) "
            "VALUES ('plan_node', 'x', 'markdown', 'again', ?)", (now,),
        )
    # Different owner_type with same owner_id → OK.
    sqlite_conn.execute(
        "INSERT INTO body (owner_type, owner_id, body_format, body_text, modification_date) "
        "VALUES ('message', 'x', 'plain', 'diff owner type', ?)", (now,),
    )
    sqlite_conn.commit()
    count = sqlite_conn.execute("SELECT COUNT(*) FROM body").fetchone()[0]
    assert count == 2


def test_node_state_event_is_append_only_log(sqlite_conn):
    now = _now()
    sqlite_conn.execute(
        "INSERT INTO roadmap (roadmap_id, title, creation_date, modification_date) "
        "VALUES ('rm', 't', ?, ?)", (now, now),
    )
    sqlite_conn.execute(
        "INSERT INTO plan_node (node_id, roadmap_id, position, node_kind, title, "
        "creation_date, modification_date) "
        "VALUES ('n1', 'rm', 1.0, 'compound', 'N', ?, ?)", (now, now),
    )
    for et in ("planned", "ready", "running", "done"):
        sqlite_conn.execute(
            "INSERT INTO node_state_event (node_id, event_type, actor, event_date) "
            "VALUES ('n1', ?, 'executor', ?)", (et, now),
        )
    sqlite_conn.commit()
    rows = sqlite_conn.execute(
        "SELECT event_type FROM node_state_event WHERE node_id='n1' ORDER BY event_id"
    ).fetchall()
    assert [r[0] for r in rows] == ["planned", "ready", "running", "done"]
