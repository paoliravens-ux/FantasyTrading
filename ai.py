"""Step 5: have Claude translate the finished numbers into plain English."""
import json
import os

import anthropic

from config import AI_MODEL

SYSTEM = """You explain fantasy football trade evaluations. All the math is already done.
Use only the numbers in the JSON you are given; do not invent stats, news, or projections.
"Points" are rest-of-season fantasy points. Write for someone deciding whether to send this trade.

Format:
Verdict: one sentence.
Why: 2-4 short bullets pointing at the lineup changes that drive the result.
Risks: 1-3 short bullets (injuries, thin depth, reliance on waiver pickups, the other side's incentive)."""


def _side(side):
    def names(players):
        return [p.name for p in players]

    return {
        "team": side.team,
        "gives": [_player(p) for p in side.gives],
        "gets": [_player(p) for p in side.gets],
        "score_before": round(side.before.total, 1),
        "score_after": round(side.after.total, 1),
        "change": round(side.change, 1),
        "starters_before": {f"{slot} {i}": p.name if p else None for i, (slot, p) in enumerate(side.before.lineup.starters)},
        "starters_after": {f"{slot} {i}": p.name if p else None for i, (slot, p) in enumerate(side.after.lineup.starters)},
        "waiver_pickups_after": names(side.after.waiver_fills + side.added),
        "players_to_drop": side.roster_overflow,
    }


def _player(p):
    return {
        "name": p.name, "position": p.position, "status": p.injury_status,
        "avg_ppg": p.avg_points, "projected_ppg": p.proj_points,
        "games_left": p.games_left, "ros_points": round(p.ros_value, 1), "vor": round(p.vor, 1),
    }


def trade_to_json(result):
    return json.dumps({"verdict": result.verdict, "me": _side(result.me), "them": _side(result.them)}, indent=2)


def explain(result):
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return "(AI explanation skipped: add ANTHROPIC_API_KEY to your .env file.)"
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
    try:
        response = _ask(client, result)
    except anthropic.AuthenticationError:
        return "(AI explanation skipped: ANTHROPIC_API_KEY in .env is missing or invalid.)"
    except anthropic.APIConnectionError:
        return "(AI explanation skipped: couldn't reach the Claude API.)"
    except anthropic.APIStatusError as e:
        return f"(AI explanation failed: {e.message})"
    if response.stop_reason == "refusal":
        return "(The AI declined to explain this trade. The numbers above are still valid.)"
    return "\n".join(block.text for block in response.content if block.type == "text")


def _ask(client, result):
    return client.beta.messages.create(
        model=AI_MODEL,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        system=SYSTEM,
        messages=[{"role": "user", "content": trade_to_json(result)}],
        # If the main model declines, the API retries on a fallback model in the same call.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
