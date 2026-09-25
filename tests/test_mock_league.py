"""Checks the worked examples from the walkthrough against the mock league."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from evaluator import evaluate_trade, verdict  # noqa: E402
from mock_data import load_mock_league  # noqa: E402
from valuation import value_league  # noqa: E402


@pytest.fixture
def data():
    return value_league(load_mock_league())


def player(data, name):
    return next(p for roster in data.teams.values() for p in roster if p.name == name)


def test_workhorse_value(data):
    p = player(data, "RB Workhorse")
    assert p.weighted_ppg == pytest.approx(17.8)
    assert p.ros_value == pytest.approx(231.4)
    assert data.replacement["RB"] == pytest.approx(89.7)
    assert p.vor == pytest.approx(141.7)


def test_special_cases(data):
    assert player(data, "WR Rookie").ros_value == pytest.approx(124.8)  # no games yet: projection only
    assert player(data, "RB Hurt").ros_value == pytest.approx(165.6)  # OUT: 13.8 x 12
    injured = player(data, "WR Injured")
    assert injured.ros_value == pytest.approx(injured.weighted_ppg * injured.games_left * 0.5)


def test_bench_trade_helps_me(data):
    a, b = data.teams["Team A"], data.teams["Team B"]
    give = [p for p in a if p.name in ("RB Backup", "WR Rookie")]
    get = [p for p in b if p.name == "RB Hurt"]
    result = evaluate_trade(data, "Team A", "Team B", give, get)
    assert result.me.after.starters_pts - result.me.before.starters_pts == pytest.approx(33.0)
    assert result.me.change == pytest.approx(28.7, abs=0.05)


def test_losing_only_te_gets_waiver_fill(data):
    a, b = data.teams["Team A"], data.teams["Team B"]
    give = [p for p in a if p.name in ("RB Workhorse", "WR Rookie")]
    get = [p for p in b if p.name == "TE Mismatch"]
    result = evaluate_trade(data, "Team A", "Team B", give, get)
    assert result.me.change < -5
    assert [p.name for p in result.them.after.waiver_fills] == ["TE Waiver"]


def test_verdicts():
    assert verdict(2, -3) == "Fair: roughly even for both teams"
    assert verdict(20, -20) == "You win, but expect pushback"
    assert verdict(-20, 20) == "Bad for you: they win this one"
