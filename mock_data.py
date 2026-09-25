"""A fake league for testing without logging in to ESPN (python main.py --mock ...)."""
from config import FINAL_WEEK
from data import count_games
from models import LeagueData, PlayerValue

CURRENT_WEEK = 5


def _player(team, name, pos, avg, proj, bye=4, status="ACTIVE", ir=False):
    weeks = {w for w in range(1, FINAL_WEEK + 1) if w != bye}
    return PlayerValue(
        name=name, position=pos, pro_team="NFL", fantasy_team=team,
        avg_points=avg, proj_points=proj,
        games_left=count_games(weeks, CURRENT_WEEK),
        injury_status=status, on_ir=ir,
    )


# (name, position, avg so far, projected per game, extra options)
ROSTERS = {
    "Team A": [
        ("QB Captain", "QB", 21.0, 20.0, {}),
        ("QB Clipboard", "QB", 14.0, 14.5, {}),
        ("RB Workhorse", "RB", 19.0, 17.5, {}),
        ("RB Steady", "RB", 14.0, 13.0, {}),
        ("RB Backup", "RB", 10.6, 10.1, {}),
        ("RB Handcuff", "RB", 5.0, 6.0, {"bye": 9}),
        ("WR Ace", "WR", 18.0, 16.5, {}),
        ("WR Solid", "WR", 13.0, 12.0, {}),
        ("WR Rookie", "WR", 0.0, 9.6, {}),  # hasn't played yet
        ("WR Depth", "WR", 8.0, 8.25, {}),
        ("TE Blocker", "TE", 7.3, 6.8, {}),
        ("K Leg", "K", 8.5, 8.0, {}),
        ("D/ST Wall", "D/ST", 7.0, 7.5, {}),
    ],
    "Team B": [
        ("QB Gunslinger", "QB", 19.5, 19.0, {}),
        ("RB Bellcow", "RB", 16.0, 15.0, {}),
        ("RB Hurt", "RB", 15.0, 13.5, {"status": "OUT"}),
        ("RB Scatback", "RB", 9.0, 9.5, {"bye": 11}),
        ("RB Vulture", "RB", 7.5, 6.5, {}),
        ("WR Alpha One", "WR", 20.0, 17.0, {}),
        ("WR Deep Threat", "WR", 12.0, 11.0, {"bye": 7}),
        ("WR Slot", "WR", 9.5, 9.0, {}),
        ("WR Possession", "WR", 8.0, 8.5, {}),
        ("TE Mismatch", "TE", 12.0, 12.5, {}),  # their only TE
        ("K Automatic", "K", 9.0, 8.5, {}),
        ("D/ST Blitz", "D/ST", 8.0, 7.0, {}),
        ("WR Injured", "WR", 14.0, 13.0, {"status": "INJURY_RESERVE", "ir": True}),
    ],
    "Team C": [
        ("QB Veteran", "QB", 17.0, 17.5, {}),
        ("RB Grinder", "RB", 13.0, 12.5, {}),
        ("RB Speedster", "RB", 11.0, 12.0, {}),
        ("RB Rotational", "RB", 7.0, 7.5, {}),
        ("WR Burner", "WR", 16.0, 15.0, {}),
        ("WR Chains", "WR", 11.5, 11.0, {}),
        ("WR Gadget", "WR", 7.5, 8.0, {}),
        ("TE Reliable", "TE", 9.5, 9.0, {}),
        ("TE Upside", "TE", 6.0, 7.0, {}),
        ("K Boomer", "K", 8.0, 8.0, {}),
        ("D/ST Swarm", "D/ST", 7.5, 7.0, {}),
    ],
}

FREE_AGENTS = [
    ("QB Streamer", "QB", 15.0, 15.5, {}),
    ("QB Journeyman", "QB", 12.0, 13.0, {}),
    ("RB Waiver", "RB", 6.5, 7.0, {}),
    ("RB Committee", "RB", 5.0, 6.0, {}),
    ("WR Waiver", "WR", 7.0, 7.5, {}),
    ("WR Fourth", "WR", 5.5, 6.0, {}),
    ("TE Waiver", "TE", 5.0, 5.5, {}),
    ("TE Blocking", "TE", 3.5, 4.0, {}),
    ("K Waiver", "K", 7.5, 7.5, {}),
    ("D/ST Waiver", "D/ST", 6.5, 6.5, {}),
]


def load_mock_league():
    teams = {
        team: [_player(team, name, pos, avg, proj, **opts) for name, pos, avg, proj, opts in roster]
        for team, roster in ROSTERS.items()
    }
    free_agents = [_player("FA", name, pos, avg, proj, **opts) for name, pos, avg, proj, opts in FREE_AGENTS]
    return LeagueData(teams=teams, free_agents=free_agents, current_week=CURRENT_WEEK)
