#!/usr/bin/env python3
"""Read-only markdown export of a roadmap graph.

Renders a roadmap and its plan_nodes as a nested directory of markdown files:

  <outdir>/
    roadmap.md                        # title + top-level summary
    index.md                          # full tree outline (table of contents)
    <compound-slug>/
      index.md                        # compound node: body + children TOC
      <primitive-slug>.md             # primitive node: body + metadata
      <nested-compound-slug>/
        index.md
        ...
    <primitive-slug>.md               # primitive at the root

The export is idempotent — running it twice produces identical output.
No DB writes; the roadmap graph is the source of truth, this is just a
projection for humans / git / review.

Usage:
  python3 roadmap_export.py <db-path> <roadmap-id> <outdir>
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(title: str) -> str:
    """Stable kebab-case slug from a title; collision-proof via node_id fallback."""
    s = _SLUG_RE.sub("-", title.lower()).strip("-")
    return s or "untitled"


@dataclass
class Node:
    node_id: str
    roadmap_id: str
    parent_id: str | None
    position: float
    node_kind: str                     # compound | primitive
    title: str
    specialist: str | None
    speciality: str | None
    body: str
    depends_on: list[str]              # node_ids of prerequisites
    latest_state: str | None           # latest node_state_event.event_type
    children: list["Node"]


def _fetch_roadmap(conn: sqlite3.Connection, roadmap_id: str) -> dict | None:
    row = conn.execute(
        "SELECT roadmap_id, title, creation_date, modification_date "
        "FROM roadmap WHERE roadmap_id = ?",
        (roadmap_id,),
    ).fetchone()
    if not row:
        return None
    return {"roadmap_id": row[0], "title": row[1],
            "creation_date": row[2], "modification_date": row[3]}


def _fetch_nodes(conn: sqlite3.Connection, roadmap_id: str) -> dict[str, Node]:
    """All plan_nodes in the roadmap, hydrated with body, deps, latest state."""
    node_rows = conn.execute(
        "SELECT node_id, roadmap_id, parent_id, position, node_kind, title, "
        "specialist, speciality FROM plan_node WHERE roadmap_id = ? "
        "ORDER BY position",
        (roadmap_id,),
    ).fetchall()
    nodes: dict[str, Node] = {}
    for r in node_rows:
        nodes[r[0]] = Node(
            node_id=r[0], roadmap_id=r[1], parent_id=r[2], position=r[3],
            node_kind=r[4], title=r[5], specialist=r[6], speciality=r[7],
            body="", depends_on=[], latest_state=None, children=[],
        )

    # Bodies.
    body_rows = conn.execute(
        "SELECT owner_id, body_text FROM body WHERE owner_type = 'plan_node'"
    ).fetchall()
    for owner_id, body_text in body_rows:
        if owner_id in nodes:
            nodes[owner_id].body = body_text

    # Dependencies — collect only those whose node_id is in this roadmap.
    node_ids = set(nodes.keys())
    dep_rows = conn.execute(
        "SELECT node_id, depends_on_id FROM node_dependency"
    ).fetchall()
    for node_id, dep_id in dep_rows:
        if node_id in node_ids:
            nodes[node_id].depends_on.append(dep_id)

    # Latest state per node.
    for node_id in node_ids:
        latest = conn.execute(
            "SELECT event_type FROM node_state_event "
            "WHERE node_id = ? ORDER BY event_id DESC LIMIT 1",
            (node_id,),
        ).fetchone()
        if latest:
            nodes[node_id].latest_state = latest[0]

    return nodes


def _build_tree(nodes: dict[str, Node]) -> list[Node]:
    """Populate children[] and return root-level nodes ordered by position."""
    roots: list[Node] = []
    for n in nodes.values():
        if n.parent_id is None:
            roots.append(n)
        elif n.parent_id in nodes:
            nodes[n.parent_id].children.append(n)
    roots.sort(key=lambda x: x.position)
    for n in nodes.values():
        n.children.sort(key=lambda x: x.position)
    return roots


def _slug_for(node: Node, used: dict[str, str]) -> str:
    """Compute a filesystem-safe slug; fall back to node_id on collision."""
    if node.node_id in used:
        return used[node.node_id]
    base = slugify(node.title)
    slug = base
    n = 1
    while slug in used.values():
        n += 1
        slug = f"{base}-{n}"
    used[node.node_id] = slug
    return slug


def _render_node_section(node: Node, slugs: dict[str, str]) -> str:
    """Metadata block shared by compound and primitive renderings."""
    lines: list[str] = [f"# {node.title}", ""]
    meta = [f"- **Kind:** {node.node_kind}"]
    if node.specialist:
        meta.append(f"- **Specialist:** {node.specialist}")
    if node.speciality:
        meta.append(f"- **Speciality:** {node.speciality}")
    if node.latest_state:
        meta.append(f"- **Latest state:** {node.latest_state}")
    if node.depends_on:
        dep_titles = [slugs.get(d, d) for d in node.depends_on]
        meta.append(f"- **Depends on:** {', '.join(dep_titles)}")
    lines.extend(meta)
    lines.append("")
    if node.body:
        lines.append(node.body.rstrip())
        lines.append("")
    return "\n".join(lines)


def _render_compound_index(node: Node, slugs: dict[str, str]) -> str:
    """index.md for a compound node: metadata + body + children TOC."""
    parts = [_render_node_section(node, slugs)]
    if node.children:
        parts.append("## Children")
        parts.append("")
        for child in node.children:
            slug = slugs[child.node_id]
            if child.node_kind == "compound":
                parts.append(f"- [{child.title}]({slug}/index.md)")
            else:
                parts.append(f"- [{child.title}]({slug}.md)")
        parts.append("")
    return "\n".join(parts)


def _write_node(node: Node, outdir: Path, slugs: dict[str, str]) -> None:
    slug = slugs[node.node_id]
    if node.node_kind == "primitive":
        (outdir / f"{slug}.md").write_text(_render_node_section(node, slugs))
        return
    # compound → subdirectory + recurse
    subdir = outdir / slug
    subdir.mkdir(exist_ok=True)
    (subdir / "index.md").write_text(_render_compound_index(node, slugs))
    for child in node.children:
        _write_node(child, subdir, slugs)


def _render_root_toc(
    roadmap: dict, roots: list[Node], slugs: dict[str, str]
) -> str:
    lines = [
        f"# {roadmap['title']}",
        "",
        f"_Roadmap `{roadmap['roadmap_id']}` — rendered from the plan_node graph._",
        "",
        "## Outline",
        "",
    ]
    def walk(nodes: list[Node], depth: int) -> None:
        for n in nodes:
            slug = slugs[n.node_id]
            prefix = "  " * depth + "- "
            if n.node_kind == "compound":
                lines.append(f"{prefix}[{n.title}]({slug}/index.md)")
            else:
                lines.append(f"{prefix}[{n.title}]({slug}.md)")
            walk(n.children, depth + 1)
    walk(roots, 0)
    lines.append("")
    return "\n".join(lines)


def _render_roadmap_md(roadmap: dict, root_count: int) -> str:
    return (
        f"# {roadmap['title']}\n"
        f"\n"
        f"- **Roadmap ID:** `{roadmap['roadmap_id']}`\n"
        f"- **Created:** {roadmap['creation_date']}\n"
        f"- **Modified:** {roadmap['modification_date']}\n"
        f"- **Top-level items:** {root_count}\n"
        f"\n"
        f"See [index.md](index.md) for the full outline.\n"
    )


def export_roadmap(
    conn: sqlite3.Connection, roadmap_id: str, outdir: Path
) -> None:
    roadmap = _fetch_roadmap(conn, roadmap_id)
    if not roadmap:
        raise ValueError(f"roadmap {roadmap_id!r} not found")

    nodes = _fetch_nodes(conn, roadmap_id)
    roots = _build_tree(nodes)

    slugs: dict[str, str] = {}
    # Assign slugs breadth-first per-parent so siblings compete for space
    # in the same namespace; cross-parent collisions resolved by counter.
    frontier: list[tuple[Node, dict[str, str]]] = [(n, slugs) for n in roots]
    # Simpler: single global slug namespace is fine for filesystems.
    def _assign_slugs(ns: list[Node]) -> None:
        for n in ns:
            _slug_for(n, slugs)
            _assign_slugs(n.children)
    _assign_slugs(roots)

    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "roadmap.md").write_text(_render_roadmap_md(roadmap, len(roots)))
    (outdir / "index.md").write_text(_render_root_toc(roadmap, roots, slugs))

    for n in roots:
        _write_node(n, outdir, slugs)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("db", type=Path, help="Path to atp.sqlite")
    parser.add_argument("roadmap_id", help="Roadmap ID to export")
    parser.add_argument("outdir", type=Path, help="Output directory")
    args = parser.parse_args(argv)

    conn = sqlite3.connect(args.db)
    try:
        export_roadmap(conn, args.roadmap_id, args.outdir)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    finally:
        conn.close()
    print(f"exported {args.roadmap_id} to {args.outdir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
