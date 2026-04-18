"""Session options (allowed_tools / max_turns / permission_mode) flow through.

The protocol carries policy to the runtime; tests here assert the
`TurnIO`/runner boundary observes the options the host passed. Actual
*enforcement* (e.g. refusing a disallowed tool) is runtime-specific and
tested separately in each runner's test suite.
"""
from __future__ import annotations

from services.integration_surface import SessionOptions

from ..fixtures.fake_team import FakeTeam


class OptionsRecordingTeam:
    def __init__(self) -> None:
        self.seen: list[SessionOptions] = []

    async def __call__(self, io, user_turn, ctx):
        self.seen.append(ctx.options)
        await io.emit("result", {"stop_reason": "end_turn"})


def test_options_reach_runner(transport_factory, run_async, collect_events):
    team = OptionsRecordingTeam()
    session = transport_factory(team)

    async def scenario():
        opts = SessionOptions(
            allowed_tools=("Read", "Grep"),
            disallowed_tools=("Bash",),
            max_turns=3,
            permission_mode="bypass",
        )
        h = await session.start(team="t", options=opts)
        await session.send(h.session_id, "hi")
        await collect_events(session, h.session_id)
        await session.close(h.session_id)

    run_async(scenario())
    assert team.seen, "runner should have been invoked"
    got = team.seen[-1]
    assert got.allowed_tools == ("Read", "Grep")
    assert got.disallowed_tools == ("Bash",)
    assert got.max_turns == 3
    assert got.permission_mode == "bypass"


def test_defaults_when_options_omitted(
    transport_factory, run_async, collect_events
):
    team = OptionsRecordingTeam()
    session = transport_factory(team)

    async def scenario():
        h = await session.start(team="t")
        await session.send(h.session_id, "hi")
        await collect_events(session, h.session_id)
        await session.close(h.session_id)

    run_async(scenario())
    got = team.seen[-1]
    assert got.allowed_tools == ()
    assert got.max_turns is None
    assert got.permission_mode == "default"
