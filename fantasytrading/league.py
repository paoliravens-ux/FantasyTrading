"""Connect to an ESPN fantasy football league using credentials from the environment."""
import os

from dotenv import load_dotenv
from espn_api.football import League


def load_league() -> League:
    load_dotenv()
    league_id = os.environ.get("ESPN_LEAGUE_ID")
    if not league_id:
        raise SystemExit("ESPN_LEAGUE_ID is not set. Copy .env.example to .env and fill it in.")
    return League(
        league_id=int(league_id),
        year=int(os.environ.get("ESPN_YEAR", "2026")),
        espn_s2=os.environ.get("ESPN_S2") or None,
        swid=os.environ.get("ESPN_SWID") or None,
    )
