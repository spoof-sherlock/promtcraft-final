"""
CREATIVIA // Hyperparameters
============================
Tweak these values to change game difficulty and behaviour.
"""

# ── Card Stats ──────────────────────────────────────────────────────────────
# Starting stat value for each of the four board cards' primary metric
STARTING_PRIMARY_STAT       = 15

# Starting value for a board card's non-primary (weak) metrics
STARTING_WEAK_STAT          = 6

# How widely randomised incoming card stats are (±spread around a base value)
INCOMING_CARD_STAT_BASE     = 6
INCOMING_CARD_STAT_SPREAD   = 4   # uniform random in [base-spread, base+spread]

# ── Synergy ──────────────────────────────────────────────────────────────────
# Synergy score range is [0, 1].  Values above HIGH_SYNERGY_THRESHOLD are
# considered high-synergy merges; below LOW_SYNERGY_THRESHOLD are harmful.
HIGH_SYNERGY_THRESHOLD      = 0.65
LOW_SYNERGY_THRESHOLD       = 0.35

# Stat multiplier applied to both cards on a high-synergy merge
HIGH_SYNERGY_BOOST          = 1.25   # +25 %
# Stat multiplier applied to both cards on a low-synergy merge (penalty)
LOW_SYNERGY_PENALTY         = 0.75   # −25 %
# Multiplier for a neutral merge (between thresholds)
NEUTRAL_SYNERGY_SCALE       = 1.00   # unchanged

# How much of the incoming card's stats are transferred to the board card
# on a merge (the board card gains: incoming_stat * MERGE_TRANSFER_RATIO)
MERGE_TRANSFER_RATIO        = 0.6

# ── Synergy Hints ────────────────────────────────────────────────────────────
# How many hint tiers are shown to the player (3 = ✦✦✦ / ✦✦○ / ✦○○)
SYNERGY_HINT_TIERS          = 3

# ── Difficulty Scaling ───────────────────────────────────────────────────────
# Every N cards dealt, incoming card quality degrades by DIFFICULTY_STEP
# (reduces INCOMING_CARD_STAT_BASE slightly, increases variance)
DIFFICULTY_RAMP_EVERY       = 8     # cards dealt between difficulty ticks
DIFFICULTY_STEP             = 0.4   # each tick reduces effective stat base

# ── Game Over ────────────────────────────────────────────────────────────────
# If ANY metric on ANY board card falls below this value, the game ends
STAT_FLOOR                  = 0

# ── Score ────────────────────────────────────────────────────────────────────
# Score = sum of all board-card stats  ×  score_multiplier
SCORE_MULTIPLIER            = 10

# ── Merge mechanics ───────────────────────────────────────────────────────────
# Fraction of the total stat gain that is drained from the board card's
# weakest metric as a trade-off cost.
# 0.0 = no cost, 1.0 = all gains immediately drained from weakest stat.
# At 0.4 a balanced card can grow steadily; a lopsided card will bleed out.
STAT_TRADEOFF_RATIO         = 0.40

# ── Timing ───────────────────────────────────────────────────────────────────
# Frames a merge animation plays before accepting new input
MERGE_ANIM_FRAMES           = 22

# Frames the game-over or victory screen holds before allowing restart
END_SCREEN_HOLD_FRAMES      = 60
