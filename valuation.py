"""Step 2: turn stats into rest-of-season value (ROS) and value over replacement (VOR)."""
from config import IR_MULTIPLIER, W_PAST, W_PROJ


def weighted_ppg(p):
    # A player who hasn't played yet has an average of 0; don't punish him for it.
    if p.avg_points <= 0:
        return p.proj_points
    return W_PAST * p.avg_points + W_PROJ * p.proj_points


def value_player(p):
    games = p.games_left
    if p.injury_status == "OUT" and games > 0:
        games -= 1
    p.weighted_ppg = weighted_ppg(p)
    p.ros_value = p.weighted_ppg * games
    if p.on_ir:
        p.ros_value *= IR_MULTIPLIER


def value_league(data):
    """Fill in weighted_ppg, ros_value and vor for every player in the league."""
    rostered = [p for roster in data.teams.values() for p in roster]
    for p in rostered + data.free_agents:
        value_player(p)

    # The replacement at each position is the best free agent you could pick up.
    data.replacement = {}
    for fa in data.free_agents:
        data.replacement[fa.position] = max(data.replacement.get(fa.position, 0.0), fa.ros_value)

    for p in rostered + data.free_agents:
        p.vor = p.ros_value - data.replacement.get(p.position, 0.0)
    return data
