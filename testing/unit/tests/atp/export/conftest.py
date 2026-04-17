"""Shared fixtures for roadmap_export tests."""
from __future__ import annotations

import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
SCRIPTS_DB = REPO_ROOT / "plugins" / "dev-team" / "scripts" / "db"
SCHEMA_PATH = SCRIPTS_DB / "schema-v3.sql"

sys.path.insert(0, str(SCRIPTS_DB))
import roadmap_export  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@pytest.fixture
def conn(tmp_path):
    db = tmp_path / "atp.db"
    c = sqlite3.connect(db)
    c.execute("PRAGMA foreign_keys = ON")
    c.executescript(SCHEMA_PATH.read_text())
    c.commit()
    yield c
    c.close()


@pytest.fixture
def export_module():
    return roadmap_export


@pytest.fixture
def now() -> str:
    return _now()


@pytest.fixture
def seed(conn, now):
    """Factory that seeds a roadmap with tree-shaped nodes + optional deps + bodies."""
    def _factory(
        roadmap_id: str = "rm",
        title: str = "Test Roadmap",
        tree: list[tuple] | None = None,     # [(node_id, parent_id, kind, title), ...]
        deps: list[tuple] | None = None,     # [(node_id, depends_on_id), ...]
        bodies: dict | None = None,          # {node_id: body_text}
    ) -> str:
        conn.execute(
            "INSERT INTO roadmap (roadmap_id, title, creation_date, modification_date) "
            "VALUES (?, ?, ?, ?)", (roadmap_id, title, now, now),
        )
        for i, (nid, parent, kind, node_title) in enumerate(tree or []):
            conn.execute(
                "INSERT INTO plan_node (node_id, roadmap_id, parent_id, position, "
                "node_kind, title, creation_date, modification_date) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (nid, roadmap_id, parent, float(i + 1), kind, node_title, now, now),
            )
        for nid, dep_id in (deps or []):
            conn.execute(
                "INSERT INTO node_dependency (node_id, depends_on_id, creation_date) "
                "VALUES (?, ?, ?)", (nid, dep_id, now),
            )
        for nid, body in (bodies or {}).items():
            conn.execute(
                "INSERT INTO body (owner_type, owner_id, body_format, body_text, "
                "modification_date) VALUES ('plan_node', ?, 'markdown', ?, ?)",
                (nid, body, now),
            )
        conn.commit()
        return roadmap_id
    return _factory
