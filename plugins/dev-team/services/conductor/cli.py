"""Conductor CLI — spec §10.1.

Walking-skeleton scope: `conductor start --session-id ... --playbook ...`.
`status`, `stop`, `resume` land in step 2.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
import uuid
from pathlib import Path
from uuid import UUID

from .arbitrator import Arbitrator
from .arbitrator.backends import SqliteBackend
from .conductor import Conductor
from .dispatcher import ClaudeCodeDispatcher, Dispatcher, MockDispatcher
from .playbook import load_playbook
from .team_lead import TeamLead


def _build_dispatcher(name: str) -> Dispatcher:
    if name == "claude-code":
        return ClaudeCodeDispatcher()
    if name == "mock":
        return MockDispatcher()
    raise SystemExit(f"Unknown dispatcher: {name}")


async def _run_start(
    session_id: UUID,
    playbook_path: Path,
    dispatcher_name: str,
    db_path: Path,
) -> int:
    playbook = load_playbook(playbook_path)
    backend = SqliteBackend(db_path)
    arbitrator = Arbitrator(backend)
    await arbitrator.start()
    try:
        dispatcher = _build_dispatcher(dispatcher_name)
        team_lead = TeamLead(playbook)
        conductor = Conductor(
            arbitrator=arbitrator,
            dispatcher=dispatcher,
            team_lead=team_lead,
            session_id=session_id,
        )
        await conductor.run()
        messages = await arbitrator.list_messages(session_id)
        for m in messages:
            print(f"[{m.type}] {m.body}")
        return 0
    finally:
        await arbitrator.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="conductor")
    sub = parser.add_subparsers(dest="command", required=True)

    p_start = sub.add_parser("start", help="Start or resume a conductor session")
    p_start.add_argument("--session-id", type=str, default=None)
    p_start.add_argument("--playbook", type=str, required=True)
    p_start.add_argument(
        "--dispatcher",
        type=str,
        default="claude-code",
        choices=["claude-code", "mock"],
    )
    p_start.add_argument(
        "--db",
        type=str,
        default=".conductor/sessions.sqlite",
    )

    args = parser.parse_args(argv)

    if args.command == "start":
        session_id = UUID(args.session_id) if args.session_id else uuid.uuid4()
        playbook_path = Path(args.playbook).resolve()
        db_path = Path(args.db).resolve()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"conductor: session {session_id}")
        return asyncio.run(
            _run_start(
                session_id=session_id,
                playbook_path=playbook_path,
                dispatcher_name=args.dispatcher,
                db_path=db_path,
            )
        )

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
