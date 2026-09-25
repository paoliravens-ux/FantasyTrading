"""Print standings and rosters: python -m fantasytrading"""
from .league import load_league


def main() -> None:
    league = load_league()
    print(f"{league.settings.name} ({league.year}), week {league.current_week}\n")
    for team in sorted(league.teams, key=lambda t: t.standing):
        print(f"{team.standing:>2}. {team.team_name}  {team.wins}-{team.losses}-{team.ties}  PF {team.points_for:.1f}")
        for p in team.roster:
            print(f"      {p.position:<4} {p.name:<26} {p.proTeam:<4} avg {p.avg_points:5.1f}  proj {p.projected_total_points:6.1f}")
        print()


if __name__ == "__main__":
    main()
