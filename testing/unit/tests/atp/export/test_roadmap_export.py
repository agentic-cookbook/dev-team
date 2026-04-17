"""roadmap_export renders plan_node graphs as nested markdown."""
from __future__ import annotations

from pathlib import Path

import pytest


def test_export_missing_roadmap_raises(conn, export_module, tmp_path):
    with pytest.raises(ValueError, match="not found"):
        export_module.export_roadmap(conn, "does-not-exist", tmp_path / "out")


def test_export_creates_roadmap_and_index_files(conn, export_module, seed, tmp_path):
    rm = seed(tree=[("a", None, "primitive", "Alpha")])
    out = tmp_path / "out"
    export_module.export_roadmap(conn, rm, out)

    assert (out / "roadmap.md").exists()
    assert (out / "index.md").exists()
    roadmap_md = (out / "roadmap.md").read_text()
    assert "Test Roadmap" in roadmap_md
    assert rm in roadmap_md


def test_export_primitive_at_root_is_leaf_md(conn, export_module, seed, tmp_path):
    rm = seed(tree=[("alpha", None, "primitive", "Alpha Feature")])
    out = tmp_path / "out"
    export_module.export_roadmap(conn, rm, out)

    leaf = out / "alpha-feature.md"
    assert leaf.exists()
    content = leaf.read_text()
    assert "# Alpha Feature" in content
    assert "**Kind:** primitive" in content


def test_export_compound_creates_directory(conn, export_module, seed, tmp_path):
    rm = seed(tree=[
        ("parent", None, "compound", "Parent"),
        ("child", "parent", "primitive", "Child"),
    ])
    out = tmp_path / "out"
    export_module.export_roadmap(conn, rm, out)

    assert (out / "parent").is_dir()
    assert (out / "parent" / "index.md").exists()
    assert (out / "parent" / "child.md").exists()


def test_export_nested_compounds(conn, export_module, seed, tmp_path):
    rm = seed(tree=[
        ("root", None, "compound", "Root"),
        ("mid", "root", "compound", "Mid"),
        ("leaf", "mid", "primitive", "Leaf"),
    ])
    out = tmp_path / "out"
    export_module.export_roadmap(conn, rm, out)

    leaf = out / "root" / "mid" / "leaf.md"
    assert leaf.exists()
    assert "# Leaf" in leaf.read_text()


def test_export_includes_body(conn, export_module, seed, tmp_path):
    rm = seed(
        tree=[("alpha", None, "primitive", "Alpha")],
        bodies={"alpha": "## Description\n\nMarkdown body for alpha."},
    )
    out = tmp_path / "out"
    export_module.export_roadmap(conn, rm, out)

    content = (out / "alpha.md").read_text()
    assert "Markdown body for alpha" in content


def test_export_notes_dependencies(conn, export_module, seed, tmp_path):
    rm = seed(
        tree=[
            ("a", None, "primitive", "Alpha"),
            ("b", None, "primitive", "Beta"),
        ],
        deps=[("b", "a")],
    )
    out = tmp_path / "out"
    export_module.export_roadmap(conn, rm, out)

    beta_content = (out / "beta.md").read_text()
    assert "Depends on" in beta_content
    assert "alpha" in beta_content


def test_export_is_idempotent(conn, export_module, seed, tmp_path):
    """Running the export twice produces byte-identical output."""
    rm = seed(tree=[
        ("root", None, "compound", "Root"),
        ("a", "root", "primitive", "Alpha"),
        ("b", "root", "primitive", "Beta"),
    ])
    out = tmp_path / "out"
    export_module.export_roadmap(conn, rm, out)
    first = {p.relative_to(out): p.read_bytes() for p in out.rglob("*.md")}

    export_module.export_roadmap(conn, rm, out)
    second = {p.relative_to(out): p.read_bytes() for p in out.rglob("*.md")}

    assert first == second


def test_export_respects_position_order(conn, export_module, seed, tmp_path):
    """Children appear in position order in the index.md TOC."""
    rm = seed(tree=[
        ("root", None, "compound", "Root"),
        ("first", "root", "primitive", "First"),
        ("second", "root", "primitive", "Second"),
        ("third", "root", "primitive", "Third"),
    ])
    out = tmp_path / "out"
    export_module.export_roadmap(conn, rm, out)

    root_index = (out / "root" / "index.md").read_text()
    first_pos = root_index.find("First")
    second_pos = root_index.find("Second")
    third_pos = root_index.find("Third")
    assert 0 < first_pos < second_pos < third_pos


def test_export_renders_latest_state(conn, export_module, seed, now, tmp_path):
    rm = seed(tree=[("alpha", None, "primitive", "Alpha")])
    # Record a state lifecycle: planned, ready, running.
    for et in ("planned", "ready", "running"):
        conn.execute(
            "INSERT INTO node_state_event (node_id, event_type, actor, event_date) "
            "VALUES ('alpha', ?, 'executor', ?)", (et, now),
        )
    conn.commit()

    out = tmp_path / "out"
    export_module.export_roadmap(conn, rm, out)

    content = (out / "alpha.md").read_text()
    assert "Latest state:" in content
    assert "running" in content
    # No stale earlier states bleed through
    assert "planned" not in content.split("Latest state:")[1].split("\n")[0]


def test_cli_exits_zero_on_success(conn, export_module, seed, tmp_path):
    import subprocess
    # We have no single-file DB entry point in sqlite3 so we write the seed
    # then point the CLI at the file.
    rm = seed(tree=[("alpha", None, "primitive", "Alpha")])
    conn.commit()
    # Copy the in-memory-ish seed to a physical path for subprocess.
    # The conn fixture already writes to tmp_path/atp.db; find it.
    db_path = tmp_path / "atp.db"
    assert db_path.exists()

    outdir = tmp_path / "md-out"
    script = Path(export_module.__file__)
    result = subprocess.run(
        ["python3", str(script), str(db_path), rm, str(outdir)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (outdir / "roadmap.md").exists()


def test_cli_exits_one_on_missing_roadmap(tmp_path, conn, export_module):
    import subprocess
    db_path = tmp_path / "atp.db"
    # Ensure file exists (fixture already created it).
    assert db_path.exists()
    script = Path(export_module.__file__)
    result = subprocess.run(
        ["python3", str(script), str(db_path), "no-such", str(tmp_path / "out")],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert "not found" in result.stderr


def test_slugify_handles_special_chars(export_module):
    assert export_module.slugify("Hello, World!") == "hello-world"
    assert export_module.slugify("  spaces  ") == "spaces"
    assert export_module.slugify("UNDER_SCORE") == "under-score"
    assert export_module.slugify("") == "untitled"
    assert export_module.slugify("!!!") == "untitled"


def test_export_avoids_slug_collisions(conn, export_module, seed, tmp_path):
    """Two nodes with the same title get distinct filenames."""
    rm = seed(tree=[
        ("a", None, "primitive", "Duplicate"),
        ("b", None, "primitive", "Duplicate"),
    ])
    out = tmp_path / "out"
    export_module.export_roadmap(conn, rm, out)

    files = sorted(p.name for p in out.iterdir() if p.suffix == ".md" and p.name not in ("roadmap.md", "index.md"))
    assert len(files) == 2
    assert files[0] != files[1]
