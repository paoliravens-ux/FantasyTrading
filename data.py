"""Step 1: download the league from ESPN and copy it onto PlayerValue forms."""
from config import (ESPN_S2, FINAL_WEEK, FREE_AGENTS_PER_POSITION, LEAGUE_ID,
                    POSITIONS, SWID, YEAR)
from models import LeagueData, PlayerValue


def count_games(weeks_with_games, current_week, final_week=FINAL_WEEK):
    """Weeks from current_week through final_week that have a game (byes don't count)."""
    return sum(1 for week in range(current_week, final_week + 1) if week in weeks_with_games)


def _games_by_pro_team(league):
    """NFL team abbreviation -> set of weeks that team plays (bye weeks are missing)."""
    from espn_api.football.constant import PRO_TEAM_MAP

    schedule = league._get_all_pro_schedule()  # {team id: {"week": [games]}}
    return {
        PRO_TEAM_MAP[team_id]: {int(week) for week, games in weeks.items() if games}
        for team_id, weeks in schedule.items()
        if team_id in PRO_TEAM_MAP
    }


def _to_player_value(player, fantasy_team, current_week, games_by_team):
    status = player.injuryStatus or "ACTIVE"
    avg = player.avg_points or 0.0
    # Season projection per game; free-agent lists sometimes only carry this week's projection.
    proj = player.projected_avg_points or getattr(player, "projected_points", 0) or avg
    return PlayerValue(
        name=player.name,
        position=player.position,
        pro_team=player.proTeam,
        fantasy_team=fantasy_team,
        avg_points=avg,
        proj_points=proj,
        games_left=count_games(games_by_team.get(player.proTeam, set()), current_week),
        injury_status=status,
        on_ir=status == "INJURY_RESERVE" or getattr(player, "lineupSlot", "") == "IR",
    )


def _free_agents(league):
    """Top free agents at each position, with full season stats when ESPN provides them."""
    listed = [p for pos in POSITIONS for p in league.free_agents(size=FREE_AGENTS_PER_POSITION, position=pos)]
    # The free-agent list only has this week's numbers; the player card has season averages.
    cards = {}
    ids = [p.playerId for p in listed]
    for i in range(0, len(ids), 50):
        try:
            found = league.player_info(playerId=ids[i:i + 50]) or []
        except Exception:
            continue
        for card in found if isinstance(found, list) else [found]:
            cards[card.playerId] = card
    return [cards.get(p.playerId, p) for p in listed]


def load_espn_league():
    from espn_api.football import League

    if not LEAGUE_ID:
        raise SystemExit("ESPN_LEAGUE_ID is not set. Copy .env.example to .env and fill it in.")
    league = League(league_id=LEAGUE_ID, year=YEAR, espn_s2=ESPN_S2, swid=SWID)
    week = league.current_week
    games = _games_by_pro_team(league)

    teams = {
        team.team_name: [_to_player_value(p, team.team_name, week, games) for p in team.roster]
        for team in league.teams
    }
    free_agents = [_to_player_value(p, "FA", week, games) for p in _free_agents(league)]
    return LeagueData(teams=teams, free_agents=free_agents, current_week=week)
