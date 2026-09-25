# FantasyTrading

Tools for analyzing trades in an ESPN fantasy football league, built on [espn_api](https://github.com/cwendt94/espn-api).

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # then fill in your league ID and, for private leagues, ESPN_S2 / ESPN_SWID
python -m fantasytrading
```

For a private league, log in at fantasy.espn.com, open DevTools → Application → Cookies, and copy the `espn_s2` and `SWID` values into `.env`. Keep `.env` out of git (it's already in `.gitignore`).
