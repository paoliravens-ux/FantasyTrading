"""Step 4: judge a trade by rebuilding both lineups before and after it."""
from dataclasses import dataclass, field

from config import BENCH_DEPTH, BENCH_WEIGHT, FAIR_THRESHOLD
from lineup import Lineup, best_lineup, eligible


@dataclass
class TeamScore:
    lineup: Lineup
    waiver_fills: list  # free agents assumed picked up to fill empty starting slots
    starters_pts: float
    bench_pts: float

    @property
    def total(self):
        return self.starters_pts + self.bench_pts


@dataclass
class SideResult:
    team: str
    gives: list
    gets: list
    before: TeamScore
    after: TeamScore
    added: list = field(default_factory=list)  # free agents added to open roster spots
    roster_overflow: int = 0  # players this team would have to drop

    @property
    def change(self):
        return self.after.total - self.before.total


@dataclass
class TradeResult:
    me: SideResult
    them: SideResult
    verdict: str


def score_roster(roster, free_agents):
    lineup = best_lineup(roster)
    on_roster = {id(p) for p in roster}
    waiver_fills = []
    starters = []
    for slot, player in lineup.starters:
        if player is None:
            # Nobody can play this slot: assume you grab the best free agent who can.
            used = on_roster | {id(p) for p in waiver_fills}
            candidates = [fa for fa in free_agents if fa.position in eligible(slot) and id(fa) not in used]
            player = max(candidates, key=lambda fa: fa.ros_value, default=None)
            if player is not None:
                waiver_fills.append(player)
        starters.append((slot, player))
    lineup = Lineup(starters=starters, bench=lineup.bench)

    starters_pts = sum(p.ros_value for _, p in starters if p is not None)
    # Depth is measured by VOR, so a backup kicker isn't worth anything.
    depth = sorted((max(0.0, p.vor) for p in lineup.bench), reverse=True)[:BENCH_DEPTH]
    return TeamScore(lineup, waiver_fills, starters_pts, BENCH_WEIGHT * sum(depth))


def evaluate_side(team, roster, gives, gets, free_agents):
    before = score_roster(roster, free_agents)
    after_roster = [p for p in roster if p not in gives] + list(gets)
    open_spots = len(roster) - len(after_roster)

    # Waiver pickups for empty starting slots use up open roster spots first.
    added = score_roster(after_roster, free_agents).waiver_fills[:max(open_spots, 0)]
    # Fill any spots still open with whichever free agent helps the most.
    for _ in range(open_spots - len(added)):
        current = after_roster + added
        base = score_roster(current, free_agents).total
        taken = {id(p) for p in current}
        best, best_gain = None, 0.0
        for fa in free_agents:
            if id(fa) in taken:
                continue
            gain = score_roster(current + [fa], free_agents).total - base
            if gain > best_gain:
                best, best_gain = fa, gain
        if best is None:
            break
        added.append(best)

    after = score_roster(after_roster + added, free_agents)
    return SideResult(team, list(gives), list(gets), before, after, added,
                      roster_overflow=max(0, -open_spots))


def verdict(mine, theirs, t=FAIR_THRESHOLD):
    if abs(mine) <= t and abs(theirs) <= t:
        return "Fair: roughly even for both teams"
    if mine > t and theirs > t:
        return "Win-win: good trade to propose"
    if mine > t and theirs < -t:
        return "You win, but expect pushback"
    if mine > t:
        return "Good for you, about even for them: they might accept"
    if abs(mine) <= t and theirs > t:
        return "About even for you, helps them"
    if abs(mine) <= t:
        return "About even for you, hurts them: they'll likely decline"
    if theirs > t:
        return "Bad for you: they win this one"
    return "Bad for both teams"


def evaluate_trade(data, my_team, their_team, give, get):
    me = evaluate_side(my_team, data.teams[my_team], give, get, data.free_agents)
    them = evaluate_side(their_team, data.teams[their_team], get, give, data.free_agents)
    return TradeResult(me, them, verdict(me.change, them.change))
