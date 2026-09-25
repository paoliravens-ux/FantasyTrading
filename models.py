"""The PlayerValue form every step reads and fills in."""
from dataclasses import dataclass, field


@dataclass(eq=False)  # compare by identity, so two players with the same name stay distinct
class PlayerValue:
    # Filled in by data.py / mock_data.py
    name: str
    position: str
    pro_team: str
    fantasy_team: str  # "FA" for free agents
    avg_points: float  # points per game so far
    proj_points: float  # ESPN's projected points per game
    games_left: int  # games from this week through FINAL_WEEK, byes skipped
    injury_status: str = "ACTIVE"
    on_ir: bool = False

    # Filled in by valuation.py
    weighted_ppg: float = 0.0
    ros_value: float = 0.0  # rest-of-season points
    vor: float = 0.0  # value over the best free agent at his position

    def __repr__(self):
        return f"{self.name} ({self.position}, {self.ros_value:.1f})"


@dataclass
class LeagueData:
    teams: dict  # team name -> list[PlayerValue]
    free_agents: list  # list[PlayerValue]
    current_week: int
    replacement: dict = field(default_factory=dict)  # position -> best free agent's ros_value
