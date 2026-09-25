"""Step 1: download the league from ESPN and copy it onto PlayerValue forms."""
from config import (ESPN_S2, FINAL_WEEK, FREE_AGENTS_PER_POSITION, LEAGUE_ID,
                    POSITIONS, SWID, YEAR)
from models import LeagueData, PlayerValue


def count_games(weeks_with_games, current_week, final_week=FINAL_WEEK):
    """Weeks from current_week through final_week that have a game (byes don't count)."""
    return sum(1 for week in range(current_week, final_week + 1) if week in weeks_with_games)


def _to_player_value(player, fantasy_team, current_week):
    weeks = {int(week) for week in player.schedule}
    status = player.injuryStatus or "ACTIVE"
    return PlayerValue(
        name=player.name,
        position=player.position,
        pro_team=player.proTeam,
        fantasy_team=fantasy_team,
        avg_points=player.avg_points or 0.0,
        proj_points=player.projected_avg_points or player.avg_points or 0.0,
        games_left=count_games(weeks, current_week),
        injury_status=status,
        on_ir=status == "INJURY_RESERVE" or player.lineupSlot == "IR",
    )


def load_espn_league():
    from espn_api.football import League

    if not LEAGUE_ID:
        raise SystemExit("ESPN_LEAGUE_ID is not set. Copy .env.example to .env and fill it in.")
    league = League(league_id=LEAGUE_ID, year=YEAR, espn_s2=ESPN_S2, swid=SWID)
    week = league.current_week

    teams = {
        team.team_name: [_to_player_value(p, team.team_name, week) for p in team.roster]
        for team in league.teams
    }
    free_agents = [
        _to_player_value(p, "FA", week)
        for pos in POSITIONS
        for p in league.free_agents(size=FREE_AGENTS_PER_POSITION, position=pos)
    ]
    return LeagueData(teams=teams, free_agents=free_agents, current_week=week)
