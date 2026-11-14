"""
CREATIVIA // Card Definitions & Synergy System
===============================================
Each card has four metrics: music, art, design, gameplay (all floats).
Cards are themed; the dominant metric determines which sprite is drawn.

Synergy between two cards is computed from how complementary their
stat profiles are — not just similarity.  High synergy = the cards'
strengths cover each other's weaknesses.
"""

from __future__ import annotations
import math
import random
from dataclasses import dataclass, field
from typing import Tuple

# ── Metric indices ──────────────────────────────────────────────────────────
METRIC_MUSIC    = 0
METRIC_ART      = 1
METRIC_DESIGN   = 2
METRIC_GAMEPLAY = 3
METRIC_NAMES    = ["MUSIC", "ART", "DESIGN", "GAMEPLAY"]
METRIC_COLORS   = [9, 11, 12, 8]   # orange, lime, cyan, red  (Pyxel palette)
METRIC_SHORT    = ["MUS", "ART", "DES", "GAM"]

# ── Card name pool ───────────────────────────────────────────────────────────
# Grouped by dominant metric so a card's personality reads through its name.
_MUSIC_NAMES    = ["Melody", "Harmony", "Rhythm", "Cadence", "Resonance",
                   "Chord", "Tempo", "Echo", "Riff", "Overture"]
_ART_NAMES      = ["Palette", "Brushstroke", "Hue", "Silhouette", "Mosaic",
                   "Pigment", "Canvas", "Gradient", "Outline", "Prism"]
_DESIGN_NAMES   = ["Blueprint", "Schema", "Nexus", "Pattern", "Module",
                   "Grid", "Vector", "Framework", "Prototype", "Lattice"]
_GAMEPLAY_NAMES = ["Mechanic", "Reflex", "Combo", "Loop", "Challenge",
                   "Reward", "Trigger", "Feedback", "Surge", "Agency"]

# Special high-tier evolved names (used when total stats cross thresholds)
_EVOLVED_NAMES  = ["Synthesis", "Convergence", "Luminary", "Opus",
                   "Revelation", "Apotheosis", "Transcendence"]

# The final card name awarded on victory
FINAL_CARD_NAME = "CREATIVIA"

# ── Synergy table ────────────────────────────────────────────────────────────
# Pairwise affinity between metric categories: 0.0 (clash) → 1.0 (perfect).
# A card tagged "music" merging with an "art" card uses SYNERGY_TABLE[0][1].
# Intentionally asymmetric feelings:
#   music  ↔ art      : great (both expressive)
#   music  ↔ design   : moderate
#   music  ↔ gameplay : good  (rhythm & interactivity)
#   art    ↔ design   : good  (visual craft)
#   art    ↔ gameplay : moderate
#   design ↔ gameplay : great (systems thinking)
SYNERGY_TABLE = [
    # music  art    design gameplay
    [  1.00, 0.85,  0.50,  0.75 ],  # music
    [  0.85, 1.00,  0.75,  0.45 ],  # art
    [  0.50, 0.75,  1.00,  0.85 ],  # design
    [  0.75, 0.45,  0.85,  1.00 ],  # gameplay
]


# ── Card dataclass ───────────────────────────────────────────────────────────
@dataclass
class Card:
    name:    str
    stats:   list[float]          # [music, art, design, gameplay]
    tier:    int        = 0       # 0 = starter, increases with merges
    merges:  int        = 0       # total times this card has been merged into

    # ---- derived ------------------------------------------------
    @property
    def dominant_metric(self) -> int:
        return int(max(range(4), key=lambda i: self.stats[i]))

    @property
    def total(self) -> float:
        return sum(self.stats)

    @property
    def sprite_name(self) -> str:
        return ["card_music", "card_art", "card_design", "card_gameplay"][self.dominant_metric]

    def category(self) -> int:
        return self.dominant_metric

    def stat_vector(self) -> list[float]:
        """Normalised stat vector (sums to 1) for synergy maths."""
        t = self.total or 1.0
        return [s / t for s in self.stats]

    def __str__(self) -> str:
        s = self.stats
        return (f"{self.name}  "
                f"M:{s[0]:.0f} A:{s[1]:.0f} D:{s[2]:.0f} G:{s[3]:.0f}")


# ── Synergy calculation ───────────────────────────────────────────────────────
def synergy(a: Card, b: Card) -> float:
    """
    Returns a float in [0, 1] representing how well cards a and b complement
    each other.

    Two components:
      1. Category affinity   – from SYNERGY_TABLE
      2. Profile complement  – how much b's strengths fill a's weaknesses
    """
    cat_score = SYNERGY_TABLE[a.category()][b.category()]

    # Complement: dot(a_weakness, b_strength)
    # a's weakness = 1 - a_norm[i],  b's strength = b_norm[i]
    a_norm = a.stat_vector()
    b_norm = b.stat_vector()
    complement = sum((1.0 - a_norm[i]) * b_norm[i] for i in range(4))
    complement = min(complement, 1.0)   # clamp; theoretical max ~1.0

    return 0.55 * cat_score + 0.45 * complement


def synergy_hint(score: float, tiers: int = 3) -> int:
    """
    Returns 0, 1, or 2 (number of filled stars out of `tiers`) as a vague hint.
    Deliberately noisy so players can't reverse-engineer exact values.
    """
    noisy = max(0.0, min(1.0, score + random.uniform(-0.08, 0.08)))
    if noisy > 0.65:
        return 2
    if noisy > 0.35:
        return 1
    return 0


# ── Merge logic ──────────────────────────────────────────────────────────────
def merge(board_card: Card, incoming: Card) -> Tuple[Card, float]:
    """
    Merge `incoming` into `board_card` in-place.
    Returns (modified board_card, synergy_score).

    Stat transfer rules:
      - Each incoming stat is added to the matching board stat, scaled by
        MERGE_TRANSFER_RATIO and the synergy multiplier.
      - Then a trade-off is applied: the total gain is partly offset by
        draining the board card's currently weakest stat.  This means you
        can never just stack one metric infinitely — growth always costs
        something somewhere.
    """
    from config import (HIGH_SYNERGY_THRESHOLD, LOW_SYNERGY_THRESHOLD,
                        HIGH_SYNERGY_BOOST, LOW_SYNERGY_PENALTY,
                        NEUTRAL_SYNERGY_SCALE, MERGE_TRANSFER_RATIO,
                        STAT_TRADEOFF_RATIO)

    syn = synergy(board_card, incoming)

    if syn >= HIGH_SYNERGY_THRESHOLD:
        multiplier = HIGH_SYNERGY_BOOST
    elif syn <= LOW_SYNERGY_THRESHOLD:
        multiplier = LOW_SYNERGY_PENALTY
    else:
        multiplier = NEUTRAL_SYNERGY_SCALE

    # Step 1: transfer stats
    gains = []
    for i in range(4):
        gained = incoming.stats[i] * MERGE_TRANSFER_RATIO * multiplier
        gains.append(gained)
        board_card.stats[i] += gained

    # Step 2: trade-off — total gain drains the weakest stat
    total_gain = sum(gains)
    drain = total_gain * STAT_TRADEOFF_RATIO
    weakest = int(min(range(4), key=lambda i: board_card.stats[i]))
    board_card.stats[weakest] = max(0.0, board_card.stats[weakest] - drain)

    board_card.merges += 1
    board_card.tier = min(6, board_card.merges // 2)
    board_card.name = _pick_evolved_name(board_card)

    return board_card, syn


# ── Factories ────────────────────────────────────────────────────────────────
def make_starter_card(metric_index: int) -> Card:
    """Create one of the four starting board cards, strong in one metric."""
    from config import STARTING_PRIMARY_STAT, STARTING_WEAK_STAT
    stats = [float(STARTING_WEAK_STAT)] * 4
    stats[metric_index] = float(STARTING_PRIMARY_STAT)
    pools = [_MUSIC_NAMES, _ART_NAMES, _DESIGN_NAMES, _GAMEPLAY_NAMES]
    name  = random.choice(pools[metric_index])
    return Card(name=name, stats=stats, tier=0)


def make_incoming_card(cards_dealt: int) -> Card:
    """
    Generate a randomised incoming card.  Difficulty scales with cards_dealt.
    """
    from config import (INCOMING_CARD_STAT_BASE, INCOMING_CARD_STAT_SPREAD,
                        DIFFICULTY_RAMP_EVERY, DIFFICULTY_STEP)

    ticks = cards_dealt // DIFFICULTY_RAMP_EVERY
    effective_base = max(2.0, INCOMING_CARD_STAT_BASE - ticks * DIFFICULTY_STEP)

    stats = []
    for _ in range(4):
        lo = max(1.0, effective_base - INCOMING_CARD_STAT_SPREAD)
        hi = effective_base + INCOMING_CARD_STAT_SPREAD
        stats.append(random.uniform(lo, hi))

    dominant = int(max(range(4), key=lambda i: stats[i]))
    pools = [_MUSIC_NAMES, _ART_NAMES, _DESIGN_NAMES, _GAMEPLAY_NAMES]
    name  = random.choice(pools[dominant])
    return Card(name=name, stats=stats, tier=0)


def _pick_evolved_name(card: Card) -> str:
    tier = min(card.tier, len(_EVOLVED_NAMES) - 1)
    if card.tier < 2:
        return card.name
    return _EVOLVED_NAMES[tier - 2]
