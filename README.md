# FantasyTrading

Judges ESPN fantasy football trades by rebuilding both teams' best lineups before and after the trade, then (optionally) has Claude explain the result in plain English.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in league ID, MY_TEAM, and for private leagues ESPN_S2 / ESPN_SWID
```

For a private league, log in at fantasy.espn.com, open DevTools → Application → Cookies, and copy `espn_s2` and `SWID` into `.env`. `.env` is in `.gitignore`, so never commit or share it.

Then open `config.py` and make `LINEUP_SLOTS` and `FINAL_WEEK` match your league.

## Usage

```bash
python main.py --mock --list                                    # every player's ROS and VOR in the fake league
python main.py --mock --team "Team B" --give "RB Workhorse" --get "WR Alpha One"
python main.py --mock --team "Team B" --give "RB Backup" "WR Rookie" --get "RB Hurt"
python main.py --team "Their Team" --give "Player A" --get "Player B" --explain   # real league + AI explanation
python -m pytest tests                                          # checks the walkthrough math
```

Names can be partial as long as they match only one player or team.

## How it works

| Step | File | What it does |
|---|---|---|
| Settings | `config.py` | Weights, lineup slots, thresholds, credentials from `.env` |
| Form | `models.py` | `PlayerValue`: the one shape every step reads |
| 1. Data | `data.py` / `mock_data.py` | ESPN (or a fake league) → `PlayerValue`s, games left, top free agents |
| 2. Value | `valuation.py` | 20/80 past/projected PPG × games left = ROS; minus best free agent = VOR |
| 3. Lineup | `lineup.py` | Greedy best lineup: dedicated slots first, flex last |
| 4. Judge | `evaluator.py` | Lineup score before vs. after for both teams, bench depth at 15%, waiver fills, verdict |
| 5. Explain | `ai.py` | Sends the finished numbers to Claude for a plain-English summary |
| Runner | `main.py` | Command-line options, name matching, the printed report |
