"""Step 3: pick the best starting lineup from a roster (greedy, dedicated slots first)."""
from dataclasses import dataclass

from config import LINEUP_SLOTS, SLOT_ELIGIBILITY


@dataclass
class Lineup:
    starters: list  # list of (slot, PlayerValue or None if nobody can fill it)
    bench: list

    @property
    def holes(self):
        return [slot for slot, player in self.starters if player is None]


def eligible(slot):
    return SLOT_ELIGIBILITY.get(slot, {slot})


def slot_order():
    """Dedicated slots (one position) first, flex-style slots last."""
    slots = [slot for slot, count in LINEUP_SLOTS.items() for _ in range(count)]
    return sorted(slots, key=lambda slot: len(eligible(slot)) > 1)


def best_lineup(roster):
    remaining = sorted(roster, key=lambda p: p.ros_value, reverse=True)
    starters = []
    for slot in slot_order():
        pick = next((p for p in remaining if p.position in eligible(slot)), None)
        if pick is not None:
            remaining.remove(pick)
        starters.append((slot, pick))
    return Lineup(starters=starters, bench=remaining)
