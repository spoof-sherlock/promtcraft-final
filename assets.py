"""
PIXELBOX // Prompt-Friendly Procedural Asset Bank (Pyxel 2.x)
=============================================================
Why are sprites and sounds written as strings here instead of a binary .pyxres file?
Because AI coding assistants can read, remix, and generate hex-string pixel art
and chiptune note strings directly from your prompts!

Pyxel 16-Color Palette Reference (Hex 0 - f):
  0: Black (#000000)      8: Red (#ff004d)
  1: Navy (#1d2b53)       9: Orange (#ffa300)
  2: Purple (#7e2553)     a: Yellow (#ffec27)
  3: Green (#008751)      b: Lime (#00e436)
  4: Brown (#ab5236)      c: Cyan (#29adff)
  5: Dark Gray (#5f574f)  d: Lavender (#83769c)
  6: Light Gray (#c2c3c7) e: Pink (#ff77a8)
  7: White (#fff1e8)      f: Peach (#ffccaa)
"""

import pyxel

# Sprite UV coordinates in Image Bank 0: (u, v, width, height)
SPRITES = {
    "bot_idle": (0, 0, 8, 8),
    "bot_run": (8, 0, 8, 8),
    "orb": (16, 0, 8, 8),
    "crate": (24, 0, 8, 8),
    "drone": (32, 0, 8, 8),
    "heart": (40, 0, 8, 8),
    "cursor": (48, 0, 8, 8),
}

# Sound channel/slot indices
SOUNDS = {
    "jump": 0,
    "pickup": 1,
    "boom": 2,
    "blip": 3,
}


def register_sprite(name: str, u: int, v: int, rows: list[str]) -> None:
    """
    Register an 8x8 (or NxN) sprite into Image Bank 0 from a list of hex strings.
    Each character in a row is a color index from '0' to 'f' ('0' is transparent by default).
    """
    pyxel.images[0].set(u, v, rows)
    SPRITES[name] = (u, v, len(rows[0]), len(rows))


def init_assets() -> None:
    """Populate Image Bank 0 and Sound Slots 0-3 with starter procedural assets."""
    # 1. Bot Idle (u=0, v=0) - Cyan/White retro robot
    register_sprite(
        "bot_idle",
        0,
        0,
        [
            "00cccc00",
            "0c7777c0",
            "0c7171c0",
            "0c7777c0",
            "00cccc00",
            "0ccbbcc0",
            "0c0cc0c0",
            "00c00c00",
        ],
    )

    # 2. Bot Run/Action frame (u=8, v=0)
    register_sprite(
        "bot_run",
        8,
        0,
        [
            "00cccc00",
            "0c7777c0",
            "0c7878c0",
            "0c7777c0",
            "00cccc00",
            "0ccffcc0",
            "00c00c00",
            "0c0000c0",
        ],
    )

    # 3. Energy Orb / Collectible (u=16, v=0)
    register_sprite(
        "orb",
        16,
        0,
        [
            "000aa000",
            "00a77a00",
            "0a7aa7a0",
            "aa7997aa",
            "aa7997aa",
            "0a7aa7a0",
            "00a77a00",
            "000aa000",
        ],
    )

    # 4. Mystery Crate / Tile Block (u=24, v=0)
    register_sprite(
        "crate",
        24,
        0,
        [
            "44444444",
            "49999994",
            "49499494",
            "49944994",
            "49944994",
            "49499494",
            "49999994",
            "44444444",
        ],
    )

    # 5. Glitch Drone / Hazard (u=32, v=0)
    register_sprite(
        "drone",
        32,
        0,
        [
            "08000080",
            "008ee800",
            "08e77e80",
            "8e7887e8",
            "8e7887e8",
            "08eeee80",
            "00800800",
            "08000080",
        ],
    )

    # 6. Heart / Status Icon (u=40, v=0)
    register_sprite(
        "heart",
        40,
        0,
        [
            "08800880",
            "88788888",
            "87888888",
            "88888888",
            "08888880",
            "00888800",
            "00088000",
            "00000000",
        ],
    )

    # 7. Crosshair Cursor (u=48, v=0)
    register_sprite(
        "cursor",
        48,
        0,
        [
            "00077000",
            "00077000",
            "00000000",
            "770aa077",
            "770aa077",
            "00000000",
            "00077000",
            "00077000",
        ],
    )

    # --- Procedural 8-Bit Chiptune Sound Effects ---
    # Notes syntax: C/D/E/F/G/A/B + optional #(sharp) + octave (0-4), or R (rest)
    # Tones: T (Triangle), S (Square), P (Pulse), N (Noise)
    # Effects: N (None), S (Slide), V (Vibrato), F (FadeOut)
    pyxel.sounds[SOUNDS["jump"]].set(
        notes="c2e2g2c3",
        tones="s",
        volumes="4",
        effects="s",
        speed=7,
    )
    pyxel.sounds[SOUNDS["pickup"]].set(
        notes="e3g3b3e4",
        tones="p",
        volumes="5",
        effects="n",
        speed=6,
    )
    pyxel.sounds[SOUNDS["boom"]].set(
        notes="c2g1e1c1",
        tones="n",
        volumes="6542",
        effects="f",
        speed=9,
    )
    pyxel.sounds[SOUNDS["blip"]].set(
        notes="a3c4",
        tones="t",
        volumes="4",
        effects="n",
        speed=5,
    )


def draw_sprite(name: str, x: float, y: float, flip_x: bool = False, colkey: int = 0) -> None:
    """Draw a named sprite from Image Bank 0. Negative width flips horizontally."""
    if name not in SPRITES:
        pyxel.rect(int(x), int(y), 8, 8, 8)
        return
    u, v, w, h = SPRITES[name]
    draw_w = -w if flip_x else w
    pyxel.blt(int(x), int(y), 0, u, v, draw_w, h, colkey)


def play_sfx(name: str, channel: int = 0) -> None:
    """Trigger a named sound effect on the given channel (0-3)."""
    if name in SOUNDS:
        pyxel.play(channel, SOUNDS[name])
