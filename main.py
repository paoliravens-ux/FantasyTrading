"""Evaluate a fantasy football trade.

Examples:
  python main.py --mock --list
  python main.py --mock --team "Team B" --give "RB Workhorse" --get "WR Alpha One"
  python main.py --team "Other Team" --give "Player A" "Player B" --get "Player C" --explain
"""
import argparse

import config
from evaluator import evaluate_trade
from valuation import value_league

MOCK_MY_TEAM = "Team A"


def find(name, options, kind):
    """Match by exact name first, then by a unique partial match (case-insensitive)."""
    key = name.lower()
    exact = [o for o in options if o.lower() == key]
    if exact:
        return exact[0]
    partial = [o for o in options if key in o.lower()]
    if len(partial) == 1:
        return partial[0]
    if not partial:
        raise SystemExit(f"No {kind} matches '{name}'. Options: {', '.join(sorted(options))}")
    raise SystemExit(f"'{name}' matches more than one {kind}: {', '.join(sorted(partial))}")


def find_players(names, roster, team):
    by_name = {p.name: p for p in roster}
    return [by_name[find(n, by_name, f"player on {team}")] for n in names]


def print_rosters(data):
    for team, roster in data.teams.items():
        print(f"\n{team}")
        for p in sorted(roster, key=lambda p: p.ros_value, reverse=True):
            flag = f" [{p.injury_status}]" if p.injury_status not in ("ACTIVE", "NORMAL") else ""
            print(f"  {p.position:<4} {p.name:<22} {p.weighted_ppg:5.1f} ppg x {p.games_left:>2}"
                  f"  ROS {p.ros_value:6.1f}  VOR {p.vor:6.1f}{flag}")
    print("\nReplacement level (best free agent ROS):")
    for pos, value in data.replacement.items():
        print(f"  {pos:<4} {value:6.1f}")


def print_side(side):
    print(f"\n== {side.team} ==")
    print(f"  Gives: {', '.join(p.name for p in side.gives)}")
    print(f"  Gets:  {', '.join(p.name for p in side.gets)}")
    print(f"  {'Slot':<5} {'Before':<30} After")
    for (slot, b), (_, a) in zip(side.before.lineup.starters, side.after.lineup.starters):
        def label(p):
            return f"{p.name} ({p.ros_value:.1f})" if p else "(empty)"
        marker = "" if a is b else "  *"
        print(f"  {slot:<5} {label(b):<30} {label(a)}{marker}")
    for p in side.after.waiver_fills:
        print(f"  Assumed waiver pickup for an empty slot: {p.name}")
    for p in side.added:
        if p not in side.after.waiver_fills:
            print(f"  Open roster spot filled with: {p.name}")
    if side.roster_overflow:
        print(f"  Roster is {side.roster_overflow} over: they'd have to drop someone from the bench.")
    b, a = side.before, side.after
    print(f"  Starters {b.starters_pts:7.1f} -> {a.starters_pts:7.1f}   "
          f"Bench {b.bench_pts:5.1f} -> {a.bench_pts:5.1f}   "
          f"Total {b.total:7.1f} -> {a.total:7.1f}   Change {side.change:+.1f}")


def main():
    parser = argparse.ArgumentParser(description="Evaluate a fantasy football trade.")
    parser.add_argument("--mock", action="store_true", help="use the fake league instead of ESPN")
    parser.add_argument("--me", help="your team name (default: MY_TEAM from .env, or Team A with --mock)")
    parser.add_argument("--team", help="the team you're trading with")
    parser.add_argument("--give", nargs="+", default=[], help="players you give")
    parser.add_argument("--get", nargs="+", default=[], help="players you get")
    parser.add_argument("--explain", action="store_true", help="ask Claude for a plain-English explanation")
    parser.add_argument("--list", action="store_true", help="print every roster with its values")
    args = parser.parse_args()

    if args.mock:
        from mock_data import load_mock_league
        data = load_mock_league()
    else:
        from data import load_espn_league
        data = load_espn_league()
    value_league(data)

    if args.list:
        print_rosters(data)
        return
    if not (args.team and args.give and args.get):
        parser.error("--team, --give and --get are required (or use --list)")

    my_team = find(args.me or (MOCK_MY_TEAM if args.mock else config.MY_TEAM) or "", data.teams, "team")
    their_team = find(args.team, data.teams, "team")
    if my_team == their_team:
        raise SystemExit("You can't trade with yourself. Set --me or MY_TEAM in .env.")
    give = find_players(args.give, data.teams[my_team], my_team)
    get = find_players(args.get, data.teams[their_team], their_team)

    result = evaluate_trade(data, my_team, their_team, give, get)
    print(f"Week {data.current_week} through week {config.FINAL_WEEK}")
    print(f"Adding up ROS values: you give {sum(p.ros_value for p in give):.1f}, "
          f"get {sum(p.ros_value for p in get):.1f}")
    print_side(result.me)
    print_side(result.them)
    print(f"\nVerdict: {result.verdict}")

    if args.explain:
        from ai import explain
        print("\n" + explain(result))


if __name__ == "__main__":
    main()
