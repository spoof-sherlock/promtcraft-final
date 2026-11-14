"""
CREATIVIA // A Merge-Crafting Game
====================================
Run:   python main.py
Mouse only — no keyboard required.

You have four board cards.  A new card appears at the top each turn.
Click a board card to merge the incoming card into it.
High-synergy merges boost all stats; low-synergy merges hurt.
Any stat reaching 0 ends the game.
Raise all stats on one card above the Transcendence threshold to birth
the Essence of Creativity and win.
"""

from __future__ import annotations
import math
import os
import random
import sys

import pyxel

# ── Local imports ─────────────────────────────────────────────────────────────
from engine import Camera, ParticleSystem, FloatingTextManager
from cards  import (Card, METRIC_NAMES, METRIC_COLORS, METRIC_SHORT,
                    make_starter_card, make_incoming_card, merge, synergy,
                    synergy_hint)
from music_player import MusicPlayer
import config as CFG

# ── Screen constants ──────────────────────────────────────────────────────────
SW, SH = 240, 180      # wider canvas for a card-game feel
FPS    = 30

# ── Layout constants ──────────────────────────────────────────────────────────
CARD_W, CARD_H = 44, 60          # pixel dimensions of one card
INCOMING_X     = SW // 2 - CARD_W // 2
INCOMING_Y     = 10
BOARD_Y        = SH - CARD_H - 14
BOARD_XS       = [10, 65, 120, 175]   # x positions of the four board slots
HINT_Y         = INCOMING_Y + CARD_H + 6

# Pyxel palette indices used throughout
COL_BG        = 1    # dark navy
COL_PANEL     = 0    # black
COL_BORDER    = 12   # cyan
COL_TEXT      = 7    # white
COL_DIM       = 5    # dark grey
COL_GOLD      = 10   # yellow
COL_GOOD      = 11   # lime
COL_BAD       = 8    # red
COL_NEUTRAL   = 6    # light grey
COL_PURPLE    = 2
COL_HOVER     = 9    # orange highlight

# ── Sprite sheet layout (all in Image Bank 0) ─────────────────────────────────
# We place 16×16 tile sprites starting at u=0,v=0 in an 8-row grid
# Card face sprites:  4 types  × 16×16 = at u=0..63, v=0..15
# Card frame:         1 frame    16×16   at u=64,  v=0
# Star sprites:       full/empty 8×8    at u=80,  v=0 / u=88, v=0
# BG tile:            two tiles  16×16  at u=96,  v=0 and u=112, v=0
# Final card art:     16×16             at u=128, v=0

SPRITE_MUSIC_U    = 0
SPRITE_ART_U      = 16
SPRITE_DESIGN_U   = 32
SPRITE_GAMEPLAY_U = 48
SPRITE_FINAL_U    = 64
SPRITE_ROW        = 0

SPRITE_STAR_FULL_U  = 80
SPRITE_STAR_EMPTY_U = 88
SPRITE_STAR_ROW     = 0

BG_TILE1_U = 96
BG_TILE2_U = 112
BG_TILE_ROW = 0


def _px(rows: list[str]) -> list[str]:
    """Pad 8-wide rows to 16 wide by doubling each pixel (for 16×16 tiles)."""
    return rows  # we define 16-wide rows directly


def register_all_sprites() -> None:
    """Write all procedural pixel art into Image Bank 0."""

    img = pyxel.images[0]

    # ── Helper: set a 16×16 block ──────────────────────────────────────────
    def put16(u: int, v: int, rows: list[str]) -> None:
        # rows must be exactly 16 strings of exactly 16 hex chars
        img.set(u, v, rows)

    def put8(u: int, v: int, rows: list[str]) -> None:
        img.set(u, v, rows)

    # ═══════════════════════════════════════════════════════════════════════
    # CARD FACE SPRITES  (16 × 16, colour index strings)
    # ═══════════════════════════════════════════════════════════════════════

    # ── MUSIC card face — musical note / headphone motif ─────────────────
    put16(SPRITE_MUSIC_U, SPRITE_ROW, [
        "0000000000000000",
        "0000009990000000",
        "0000099f990000000"[:16],
        "0000099ff9900000",
        "0000099990000000",
        "0000099000000000",
        "0000990000000000",
        "0009990000000000",
        "0009900000000000",
        "0009900090000000",
        "0009900090000000",
        "0009900090000000",
        "0009999990000000",
        "0000999900000000",
        "0000000000000000",
        "0000000000000000",
    ])

    # ── ART card face — painter's palette + brush ─────────────────────────
    put16(SPRITE_ART_U, SPRITE_ROW, [
        "0000000000000000",
        "0000bbb000000000",
        "000b888b00000000",
        "00b88888b0000000",
        "00b8b88bb0000000",
        "00b888888000e000",
        "00b888b8b00ee000",
        "000b888b000ee000",
        "0000bbb0000e0000",
        "0000000000e00000",
        "000000000e000000",
        "0000000000000000",
        "0000000000000000",
        "0000000000000000",
        "0000000000000000",
        "0000000000000000",
    ])

    # ── DESIGN card face — circuit / blueprint grid motif ─────────────────
    put16(SPRITE_DESIGN_U, SPRITE_ROW, [
        "0000000000000000",
        "0cccccccccccc000",
        "0c000000000cc000",
        "0c0cc000cc0cc000",
        "0c0cc000cc0cc000",
        "0c000000000c0000",
        "0c0cccccccc0c000",
        "0c000000000c0000",
        "0c0ccc00ccc0c000",
        "0c000000000c0000",
        "0cccccccccccc000",
        "000c000000c00000",
        "000cc0000cc00000",
        "00007777770000000"[:16],
        "0000000000000000",
        "0000000000000000",
    ])

    # ── GAMEPLAY card face — controller / joystick ────────────────────────
    put16(SPRITE_GAMEPLAY_U, SPRITE_ROW, [
        "0000000000000000",
        "0000088880000000",
        "0008888888800000",
        "0088888888880000",
        "0088870878880000",
        "0088888888880000",
        "0088870878880000",
        "0088888888880000",
        "0088888888880000",
        "0008888888800000",
        "0000888888000000",
        "0000088880000000",
        "0000000000000000",
        "0000000000000000",
        "0000000000000000",
        "0000000000000000",
    ])

    # ── FINAL card face — radiant star / eye of creativity ────────────────
    put16(SPRITE_FINAL_U, SPRITE_ROW, [
        "000000a000000000",
        "000000a000000000",
        "00000aaa00000000",
        "0a0aaaaaaa0a0000",
        "00aaafaaaaa00000",
        "000afffffaa00000",
        "00aaafaaaaa00000",
        "0a0aaaaaaa0a0000",
        "00000aaa00000000",
        "000000a000000000",
        "000000a000000000",
        "0000000000000000",
        "0000000000000000",
        "0000000000000000",
        "0000000000000000",
        "0000000000000000",
    ])

    # ═══════════════════════════════════════════════════════════════════════
    # STAR SPRITES  (8 × 8)
    # ═══════════════════════════════════════════════════════════════════════
    put8(SPRITE_STAR_FULL_U, SPRITE_STAR_ROW, [
        "00a00a00",
        "0aaaa000",
        "aaaaaaa0",
        "aaaaaaa0",
        "0aaaaaa0",
        "00aaaa00",
        "000aa000",
        "0000a000",
    ])

    put8(SPRITE_STAR_EMPTY_U, SPRITE_STAR_ROW, [
        "00500500",
        "05000050",
        "50000005",
        "50000005",
        "05000050",
        "00500500",
        "00055000",
        "00005000",
    ])

    # ═══════════════════════════════════════════════════════════════════════
    # BACKGROUND TILES  (16 × 16)
    # ═══════════════════════════════════════════════════════════════════════
    # Tile 1 — dark star-field tile
    put16(BG_TILE1_U, BG_TILE_ROW, [
        "1111111111111111",
        "1111711111111111",
        "1111111111171111",
        "1111111111111111",
        "1711111111111111",
        "1111111711111111",
        "1111111111111111",
        "1111111111111171",
        "1111111111111111",
        "1111171111111111",
        "1111111111111111",
        "1111111111171111",
        "1711111111111111",
        "1111111111111111",
        "1111111711111111",
        "1111111111111111",
    ])

    # Tile 2 — magical rune circle tile
    put16(BG_TILE2_U, BG_TILE_ROW, [
        "1111111111111111",
        "1111122221111111",
        "1112111112111111",
        "1121111121111111",
        "1211111112111111",
        "1211211112111211",
        "1211111111111211",
        "1211111111111211",
        "1211111112111211",
        "1211111121111111",
        "1121111112111111",
        "1112111121111111",
        "1111222211111111",
        "1111111111111111",
        "1111111111111111",
        "1111111111111111",
    ])


# ═══════════════════════════════════════════════════════════════════════════════
# Drawing helpers
# ═══════════════════════════════════════════════════════════════════════════════

def draw_bg() -> None:
    """Tile the magical starfield background."""
    tw = 16
    for ty in range(0, SH, tw):
        for tx in range(0, SW, tw):
            # Checkerboard of two bg tiles based on position parity
            use_tile2 = ((tx // tw) + (ty // tw)) % 7 == 0
            u = BG_TILE2_U if use_tile2 else BG_TILE1_U
            pyxel.blt(tx, ty, 0, u, BG_TILE_ROW, tw, tw, 0)

    # Animated shimmer: randomly light a pixel every few frames
    if pyxel.frame_count % 3 == 0:
        for _ in range(4):
            sx = random.randint(0, SW - 1)
            sy = random.randint(0, SH - 1)
            pyxel.pset(sx, sy, 7)


def draw_card(x: int, y: int, card: Card,
              hovered: bool = False,
              selected: bool = False,
              incoming: bool = False) -> None:
    """Draw a full card at pixel position (x, y)."""
    bord = COL_HOVER if hovered else (COL_BORDER if incoming else COL_DIM)
    bg   = 1 if not hovered else 0

    # Card shadow
    pyxel.rect(x + 2, y + 2, CARD_W, CARD_H, 0)
    # Card body
    pyxel.rect(x, y, CARD_W, CARD_H, bg)
    # Card border (double for selected/incoming)
    pyxel.rectb(x, y, CARD_W, CARD_H, bord)
    if incoming or selected:
        pyxel.rectb(x + 1, y + 1, CARD_W - 2, CARD_H - 2, bord)

    # Card sprite (16×16, centred horizontally, near top)
    sprite_u_map = {
        "card_music":    SPRITE_MUSIC_U,
        "card_art":      SPRITE_ART_U,
        "card_design":   SPRITE_DESIGN_U,
        "card_gameplay": SPRITE_GAMEPLAY_U,
    }
    su = sprite_u_map.get(card.sprite_name, SPRITE_MUSIC_U)
    sprite_x = x + (CARD_W - 16) // 2
    sprite_y = y + 3
    pyxel.blt(sprite_x, sprite_y, 0, su, SPRITE_ROW, 16, 16, 0)

    # Card name (truncated)
    name = card.name[:7]
    nx   = x + CARD_W // 2 - len(name) * 2
    pyxel.text(nx, sprite_y + 17, name, COL_TEXT)

    # Stat bars (4 metrics)
    bar_x  = x + 3
    bar_y0 = sprite_y + 25
    bar_w  = CARD_W - 6   # max bar width in pixels
    for i, (stat, col) in enumerate(zip(card.stats, METRIC_COLORS)):
        by = bar_y0 + i * 8
        # Label
        pyxel.text(bar_x, by, METRIC_SHORT[i], COL_DIM)
        # Bar background
        bx = bar_x + 13
        pyxel.rect(bx, by, bar_w - 13, 4, 0)
        # Bar fill — clamp display to [0, 80] range
        fill_pct = max(0.0, min(1.0, stat / 80.0))
        fill_w   = max(1, int((bar_w - 13) * fill_pct)) if stat > 0 else 0
        bar_col  = COL_BAD if stat < 5 else col
        if fill_w > 0:
            pyxel.rect(bx, by, fill_w, 4, bar_col)
        # Numeric value (small, right of bar)
        val_str = f"{int(stat):2d}"
        pyxel.text(bx + bar_w - 12, by, val_str, COL_DIM)

    # Tier badge
    tier_str = f"T{card.tier}"
    pyxel.text(x + CARD_W - 10, y + 2, tier_str, COL_NEUTRAL)


def draw_synergy_stars(x: int, y: int, hint: int) -> None:
    """Draw 2-star synergy hint (filled = gold, empty = dim)."""
    for i in range(2):
        sx  = x + i * 10
        col = COL_GOLD if i < hint else COL_DIM
        # Draw a tiny star manually (5×5)
        pyxel.pset(sx + 2, sy := y,     col)
        pyxel.pset(sx + 1, sy + 1,      col)
        pyxel.pset(sx + 2, sy + 1,      col)
        pyxel.pset(sx + 3, sy + 1,      col)
        pyxel.rect(sx,     sy + 2, 5, 1, col)
        pyxel.pset(sx + 1, sy + 3,      col)
        pyxel.pset(sx + 3, sy + 3,      col)
        pyxel.pset(sx,     sy + 4,      col)
        pyxel.pset(sx + 4, sy + 4,      col)


def draw_hint_row(hints: list[int]) -> None:
    """Draw synergy hint stars below the incoming card for each board slot."""
    label_y = HINT_Y
    for slot_i, h in enumerate(hints):
        cx = BOARD_XS[slot_i] + CARD_W // 2
        # Arrow line
        pyxel.line(INCOMING_X + CARD_W // 2, INCOMING_Y + CARD_H + 2,
                   cx, BOARD_Y - 2, COL_DIM)
        # Stars
        draw_synergy_stars(cx - 10, label_y, h)


# ═══════════════════════════════════════════════════════════════════════════════
# Game States
# ═══════════════════════════════════════════════════════════════════════════════
STATE_MENU    = "menu"
STATE_PLAY    = "play"
STATE_MERGE   = "merge"
STATE_GAMEOVER= "gameover"


class Creativia:
    # ── Init ─────────────────────────────────────────────────────────────────
    def __init__(self) -> None:
        pyxel.init(SW, SH, title="CREATIVIA", fps=FPS)
        pyxel.mouse(True)

        register_all_sprites()
        self._init_sfx()

        # Music
        here = os.path.dirname(os.path.abspath(__file__))
        tracks = [os.path.join(here, f"music{i}.mp3") for i in range(1, 5)]
        self.music = MusicPlayer(tracks)
        self.music.start()

        self.camera   = Camera()
        self.particles= ParticleSystem()
        self.popups   = FloatingTextManager()

        self.high_score = 0
        self._reset()
        pyxel.run(self.update, self.draw)

    def _init_sfx(self) -> None:
        # slot 0 – merge success
        pyxel.sounds[0].set("e3g3b3e4", "p", "5432", "n", 6)
        # slot 1 – merge negative
        pyxel.sounds[1].set("b2g2d2b1", "s", "5432", "f", 8)
        # slot 2 – card dealt / blip
        pyxel.sounds[2].set("a3c4",     "t", "44",   "n", 5)
        # slot 3 – game over
        pyxel.sounds[3].set("c2a1f1c1", "n", "6542", "f", 10)
        # slot 4 – victory
        pyxel.sounds[4].set("c3e3g3c4e4g4c4", "p", "7654321", "n", 7)

    def _reset(self) -> None:
        self.state          = STATE_MENU
        self.board: list[Card] = [make_starter_card(i) for i in range(4)]
        self.incoming: Card | None = None
        self.cards_dealt    = 0
        self.score          = 0
        self.merge_anim     = 0      # countdown frames
        self.merge_slot     = -1     # which slot was targeted
        self.last_syn_score = 0.5
        self.end_hold       = 0

        # Synergy hints for current incoming card vs each board slot
        self.hints: list[int] = [1, 1, 1, 1]

        # Snapshot of board at game-over for the results screen
        self.final_board: list[Card] = []

        self.particles = ParticleSystem()
        self.popups    = FloatingTextManager()
        self.camera    = Camera()

        self._deal_next()

    # ── Dealing ───────────────────────────────────────────────────────────────
    def _deal_next(self) -> None:
        self.incoming = make_incoming_card(self.cards_dealt)
        self.cards_dealt += 1
        self._refresh_hints()
        pyxel.play(2, 2)   # blip

    def _refresh_hints(self) -> None:
        if self.incoming is None:
            self.hints = [0, 0, 0, 0]
            return
        self.hints = [synergy_hint(synergy(self.incoming, bc))
                      for bc in self.board]

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self) -> None:
        self.camera.update()
        self.particles.update(gravity=0.0)
        self.popups.update()

        if self.state == STATE_MENU:
            self._update_menu()
        elif self.state == STATE_PLAY:
            self._update_play()
        elif self.state == STATE_MERGE:
            self._update_merge_anim()
        elif self.state == STATE_GAMEOVER:
            self._update_end()

    def _update_menu(self) -> None:
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self._reset()
            self.state = STATE_PLAY

    def _update_play(self) -> None:
        if self.incoming is None:
            self._deal_next()
            return

        mx, my = pyxel.mouse_x, pyxel.mouse_y

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            for slot_i, bx in enumerate(BOARD_XS):
                by = BOARD_Y
                if bx <= mx <= bx + CARD_W and by <= my <= by + CARD_H:
                    self._do_merge(slot_i)
                    return

    def _do_merge(self, slot_i: int) -> None:
        bc = self.board[slot_i]
        inc= self.incoming
        if inc is None:
            return

        # Compute synergy before merge for feedback
        syn_val = synergy(inc, bc)
        self.last_syn_score = syn_val

        # Perform merge
        merge(bc, inc)

        # Particle burst colour based on outcome
        bx_center = BOARD_XS[slot_i] + CARD_W // 2
        by_center  = BOARD_Y + CARD_H // 2
        if syn_val >= CFG.HIGH_SYNERGY_THRESHOLD:
            self.particles.burst(bx_center, by_center,
                                 count=22, colors=[10, 11, 7], speed=2.5)
            self.popups.spawn("SYNERGY!", bx_center - 16, by_center - 20,
                              color=11, life=35)
            self.camera.shake(frames=5, intensity=1.5)
            pyxel.play(0, 0)
        elif syn_val <= CFG.LOW_SYNERGY_THRESHOLD:
            self.particles.burst(bx_center, by_center,
                                 count=18, colors=[8, 9, 5], speed=2.0)
            self.popups.spawn("CLASH!", bx_center - 10, by_center - 20,
                              color=8, life=35)
            self.camera.shake(frames=8, intensity=2.5)
            pyxel.play(1, 1)
        else:
            self.particles.burst(bx_center, by_center,
                                 count=10, colors=[12, 7], speed=1.8)
            pyxel.play(0, 0)

        self.merge_slot  = slot_i
        self.merge_anim  = CFG.MERGE_ANIM_FRAMES
        self.incoming    = None
        self.state       = STATE_MERGE

        # Update score
        self.score = int(sum(sum(c.stats) for c in self.board)
                         * CFG.SCORE_MULTIPLIER)

    def _update_merge_anim(self) -> None:
        self.merge_anim -= 1
        if self.merge_anim <= 0:
            # Check game-over: any stat on any board card at or below floor
            for c in self.board:
                if any(s <= CFG.STAT_FLOOR for s in c.stats):
                    self.state    = STATE_GAMEOVER
                    self.end_hold = CFG.END_SCREEN_HOLD_FRAMES
                    self.music.stop()
                    # Snapshot board for results screen
                    import copy
                    self.final_board = copy.deepcopy(self.board)
                    if self.score > self.high_score:
                        self.high_score = self.score
                    pyxel.play(3, 3)
                    self.camera.flash(frames=6, color=8)
                    return

            self._deal_next()
            self.state = STATE_PLAY

    def _update_end(self) -> None:
        if self.end_hold > 0:
            self.end_hold -= 1
            return
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.music.start()
            self._reset()
            self.state = STATE_PLAY

    # ── Draw ─────────────────────────────────────────────────────────────────
    def draw(self) -> None:
        # Flash effect
        if self.camera.flash_frames > 0:
            pyxel.cls(self.camera.flash_color)
            return

        draw_bg()
        cam_x, cam_y = self.camera.get_offset()

        if self.state == STATE_MENU:
            self._draw_menu()
        elif self.state in (STATE_PLAY, STATE_MERGE):
            self._draw_game(cam_x, cam_y)
        elif self.state == STATE_GAMEOVER:
            self._draw_game(cam_x, cam_y)
            self._draw_gameover()

        # Particles & popups always on top
        self.particles.draw(cam_x, cam_y)
        self.popups.draw(cam_x, cam_y)

    def _draw_menu(self) -> None:
        # Dark vignette panel
        pyxel.rect(20, 20, SW - 40, SH - 30, 0)
        pyxel.rectb(20, 20, SW - 40, SH - 30, COL_BORDER)
        pyxel.rectb(21, 21, SW - 42, SH - 32, COL_PURPLE)

        # Title
        title = "CREATIVIA"
        tx = SW // 2 - len(title) * 3
        pyxel.text(tx - 1, 28, title, 0)
        pyxel.text(tx,     28, title, COL_GOLD)

        sub = "A MERGE-CRAFTING GAME"
        sx  = SW // 2 - len(sub) * 2
        pyxel.text(sx, 38, sub, COL_BORDER)

        lines = [
            "Merge incoming cards into",
            "your four board cards.",
            "High synergy boosts stats.",
            "Low synergy hurts them.",
            "Merging shifts stats:",
            "gains come at a cost.",
            "Any stat hitting ZERO",
            "ends the game.",
            "How long can you last?",
        ]
        for i, ln in enumerate(lines):
            lx = SW // 2 - len(ln) * 2
            col = COL_DIM if i in (4, 5) else COL_TEXT
            pyxel.text(lx, 50 + i * 8, ln, col)

        blink = (pyxel.frame_count // 15) % 2 == 0
        if blink:
            cta = "CLICK ANYWHERE TO START"
            pyxel.text(SW // 2 - len(cta) * 2, 50 + 9 * 8 + 6, cta, COL_GOLD)

    def _draw_game(self, cam_x: float, cam_y: float) -> None:
        mx, my = pyxel.mouse_x, pyxel.mouse_y

        # ── HUD top bar ──────────────────────────────────────────────────────
        pyxel.rect(0, 0, SW, 8, 0)
        pyxel.text(2, 1, f"SCORE:{self.score:06d}", COL_GOLD)
        pyxel.text(SW - 72, 1, f"CARDS:{self.cards_dealt:04d}", COL_DIM)
        track_lbl = f"MUS {self.music.current_track_index() + 1}/4"
        pyxel.text(SW - 24, 1, track_lbl, COL_PURPLE)

        # ── Incoming card ────────────────────────────────────────────────────
        if self.incoming is not None:
            # Header label
            lbl = "INCOMING CARD"
            pyxel.text(INCOMING_X + CARD_W // 2 - len(lbl) * 2,
                       INCOMING_Y - 7, lbl, COL_BORDER)
            draw_card(INCOMING_X, INCOMING_Y, self.incoming,
                      incoming=True, hovered=False)

        # ── Synergy hint arrows ──────────────────────────────────────────────
        if self.incoming is not None and self.state == STATE_PLAY:
            for slot_i, bx in enumerate(BOARD_XS):
                cx = bx + CARD_W // 2
                # Arrow from bottom of incoming to top of board card
                pyxel.line(INCOMING_X + CARD_W // 2,
                           INCOMING_Y + CARD_H + 1,
                           cx, BOARD_Y - 1, COL_DIM)
                # Stars
                draw_synergy_stars(cx - 10, HINT_Y, self.hints[slot_i])

        # ── Board cards ──────────────────────────────────────────────────────
        brd_lbl = "YOUR BOARD"
        pyxel.text(SW // 2 - len(brd_lbl) * 2,
                   BOARD_Y - 10, brd_lbl, COL_DIM)

        for slot_i, bx in enumerate(BOARD_XS):
            by = BOARD_Y
            hovered = (self.state == STATE_PLAY and
                       bx <= mx <= bx + CARD_W and by <= my <= by + CARD_H)
            selected = (self.state == STATE_MERGE and
                        slot_i == self.merge_slot and
                        self.merge_anim > CFG.MERGE_ANIM_FRAMES // 2)
            draw_card(bx, by, self.board[slot_i],
                      hovered=hovered, selected=selected)

        # ── Merge animation flash on target slot ─────────────────────────────
        if self.state == STATE_MERGE and self.merge_slot >= 0:
            prog = self.merge_anim / CFG.MERGE_ANIM_FRAMES
            if prog > 0.5:
                flash_alpha = int((prog - 0.5) * 2 * 8)
                col = COL_GOOD if self.last_syn_score >= CFG.HIGH_SYNERGY_THRESHOLD else (
                      COL_BAD  if self.last_syn_score <= CFG.LOW_SYNERGY_THRESHOLD  else COL_BORDER)
                bx = BOARD_XS[self.merge_slot]
                pyxel.rectb(bx - 1, BOARD_Y - 1, CARD_W + 2, CARD_H + 2, col)

        # ── Synergy legend (bottom bar) ───────────────────────────────────────
        pyxel.rect(0, SH - 8, SW, 8, 0)
        pyxel.text(2, SH - 7, "SYNERGY:", COL_DIM)
        draw_synergy_stars(42, SH - 7, 2)
        pyxel.text(56, SH - 7, "HIGH", COL_GOOD)
        draw_synergy_stars(80, SH - 7, 1)
        pyxel.text(94, SH - 7, "MED", COL_BORDER)
        draw_synergy_stars(114, SH - 7, 0)
        pyxel.text(128, SH - 7, "LOW", COL_BAD)
        pyxel.text(SW - 60, SH - 7, "SURVIVE!", COL_DIM)

    def _draw_gameover(self) -> None:
        # Full-screen results panel
        pyxel.rect(0, 0, SW, SH, 0)
        pyxel.rectb(0, 0, SW, SH, COL_BAD)
        pyxel.rectb(1, 1, SW - 2, SH - 2, COL_PURPLE)

        # Title
        hd = "GAME  OVER"
        pyxel.text(SW // 2 - len(hd) * 3, 8, hd, COL_BAD)
        pyxel.text(SW // 2 - len(hd) * 3 - 1, 7, hd, 2)

        # Score block
        is_best = self.score >= self.high_score
        sc_col  = COL_GOLD if is_best else COL_TEXT
        sc = f"SCORE  {self.score:06d}"
        pyxel.text(SW // 2 - len(sc) * 2, 20, sc, sc_col)
        if is_best:
            best = "NEW BEST!"
            pyxel.text(SW // 2 - len(best) * 2, 28, best, COL_GOLD)

        hs = f"BEST   {self.high_score:06d}"
        pyxel.text(SW // 2 - len(hs) * 2, 36, hs, COL_DIM)

        cd = f"CARDS MERGED: {self.cards_dealt}"
        pyxel.text(SW // 2 - len(cd) * 2, 44, cd, COL_NEUTRAL)

        # Divider
        pyxel.line(10, 53, SW - 10, 53, COL_DIM)

        # Per-card final stats
        pyxel.text(SW // 2 - 24, 56, "FINAL BOARD", COL_DIM)

        board = self.final_board if self.final_board else self.board
        col_w = (SW - 20) // 4   # width per card column
        for ci, card in enumerate(board):
            cx = 10 + ci * col_w
            cy = 64
            # Card name
            name = card.name[:6]
            pyxel.text(cx + col_w // 2 - len(name) * 2, cy, name, COL_TEXT)
            # Four stat bars, stacked
            bar_max_w = col_w - 4
            for mi in range(4):
                by = cy + 8 + mi * 10
                val = card.stats[mi]
                col = METRIC_COLORS[mi]
                # Short label
                pyxel.text(cx, by, METRIC_SHORT[mi][0], COL_DIM)
                # Bar background
                pyxel.rect(cx + 6, by, bar_max_w - 6, 4, 5)
                fill = max(0, int((bar_max_w - 6) * min(val / 80.0, 1.0)))
                bar_col = COL_BAD if val <= 0 else col
                if fill > 0:
                    pyxel.rect(cx + 6, by, fill, 4, bar_col)
                # Value
                pyxel.text(cx + 6, by + 5, f"{int(val)}", COL_DIM)

        # Divider
        pyxel.line(10, SH - 20, SW - 10, SH - 20, COL_DIM)

        # Prompt
        blink = (pyxel.frame_count // 15) % 2 == 0
        if self.end_hold == 0 and blink:
            rt = "CLICK TO PLAY AGAIN"
            pyxel.text(SW // 2 - len(rt) * 2, SH - 14, rt, COL_GOLD)


# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    Creativia()
