"""Settings page: every adjustable number lives here."""
import os

from dotenv import load_dotenv

load_dotenv()

# --- ESPN login (read from .env, never typed here) ---
LEAGUE_ID = int(os.environ.get("ESPN_LEAGUE_ID") or 0)
YEAR = int(os.environ.get("ESPN_YEAR") or 2026)
ESPN_S2 = os.environ.get("ESPN_S2") or None
SWID = os.environ.get("ESPN_SWID") or None
MY_TEAM = os.environ.get("MY_TEAM") or None  # your team name in the real league

# --- Season ---
FINAL_WEEK = 17  # last week that counts (end of your fantasy playoffs)

# --- Valuation (Step 2) ---
W_PAST = 0.2  # weight on points per game so far
W_PROJ = 0.8  # weight on ESPN's projected points per game
IR_MULTIPLIER = 0.5  # players on injured reserve keep this share of their value
FREE_AGENTS_PER_POSITION = 30

# --- Lineup (Step 3) ---
# How many of each slot your league starts. Match these to your ESPN league settings.
LINEUP_SLOTS = {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1, "D/ST": 1, "K": 1}
# Which positions can play each slot. A slot not listed only takes its own position.
SLOT_ELIGIBILITY = {"FLEX": {"RB", "WR", "TE"}, "OP": {"QB", "RB", "WR", "TE"}}
POSITIONS = ["QB", "RB", "WR", "TE", "D/ST", "K"]

# --- Trade scoring (Step 4) ---
BENCH_DEPTH = 3  # how many bench players count toward depth
BENCH_WEIGHT = 0.15  # each of them counts at this share of his VOR
FAIR_THRESHOLD = 5.0  # score changes within +/- this many points count as even

# --- AI explanation (Step 5) ---
AI_MODEL = "claude-opus-5"
