# PIXELBOX // Starter Seed Codebase

**PIXELBOX** is a lightweight, unfinished 160×120 retro micro-engine built on [Pyxel](https://github.com/kitao/pyxel) ([User Guide](https://kitao.github.io/pyxel/web/user-guide/)). It gives you a working 30 FPS loop, basic physics, procedural sprites, 8-bit sound effects, and camera juice—without a game loop, win/loss condition, or domain theme.

> **Finalists:** See [`PARTICIPANT_RULES.md`](PARTICIPANT_RULES.md) for challenge rules and submission requirements. Before submitting your GitHub repo, replace or update this `README.md` with your own project overview, screenshots, and **PromptCraft** section.

---

## 1. Setup & Running (macOS, Windows & Linux)

Requires Python 3.8+.

```bash
pip install -r requirements.txt
python main.py
```
*(Or run `pyxel run main.py`)*

---

## 2. Codebase Architecture

```text
pixelbox_starter/
├── main.py               # Entry point, 30 FPS loop, input handling, sandbox state
├── engine.py             # Reusable Entity, Particle, FloatingText, and Camera classes
├── assets.py             # Text-based 16-color sprites and 8-bit chiptune sound bank
├── requirements.txt      # Pyxel dependency
└── PARTICIPANT_RULES.md  # Rules, deliverables, and judging criteria
```

### `main.py` — The Sandbox Loop (`PixelBoxSandbox`)
- Initializes a `160x120` pixel window at `30 FPS` and calls `init_assets()`.
- **`update()`** runs 30 times per second:
  - Reads keyboard/gamepad input (`_update_player_input`) in either **Top-Down Mode** (8-way movement + `SPACE` radial shockwave) or **Gravity Mode** (horizontal movement + gravity + `SPACE`/`W`/`UP` jump, toggled via `G`).
  - Reads mouse input (`_update_mouse_sandbox`) to spawn crates/orbs on Left Click and detonate nearby objects on Right Click.
  - Updates items, applies friction/wall bounds, and checks player–orb collisions.
- **`draw()`** renders the grid, arena border, shockwave ring, entities, particles, floating labels, HUD bars, custom pixel cursor, and an optional telemetry/palette overlay (`TAB`).

### `engine.py` — Core Primitives
- **`Entity`**: Dataclass for 2D actors with position (`x, y`), velocity (`vx, vy`), bounding box (`w, h`), `sprite` name, `tag`, `hp`, `alive`, and an open `data` dict. Includes `.intersects(other)` for AABB collision detection and `.center()`.
- **`ParticleSystem`**: Emits and updates colored pixel bursts (`burst(x, y, count, colors, speed, life)`).
- **`FloatingTextManager`**: Spawns rising pixel text popups with a 1px drop shadow (`spawn(text, x, y, color, life)`).
- **`Camera`**: Manages viewport offsets (`cam_x, cam_y`), screen shake (`shake(frames, intensity)`), and full-screen flashes (`flash(frames, color)`).

### `assets.py` — Procedural Sprites & Audio
Instead of binary `.pyxres` files, all starter visuals and sounds are stored as **human- and AI-readable Python strings**:
- **Sprites (`register_sprite` / `draw_sprite`):** Defined as lists of 8×8 hex-character strings (`"0"`–`"f"`), where each character maps to Pyxel's 16-color palette (`"0"` is transparent black). Starter sprites: `bot_idle`, `bot_run`, `orb`, `crate`, `drone`, `heart`, `cursor`.
- **Sounds (`play_sfx`):** Defined on Pyxel sound slots `0–3` using note strings (e.g. `"c2e2g2c3"`), waveforms (`T` Triangle, `S` Square, `P` Pulse, `N` Noise), volumes, and effects. Starter sounds: `jump`, `pickup`, `boom`, `blip`.

---

## 3. Starter Controls

| Input | Action |
| :--- | :--- |
| **Arrow Keys / WASD** | Move the bot |
| **SPACE** | Shockwave pulse (Top-Down) / Jump (Gravity Mode) |
| **Left Click** | Spawn a crate at cursor (`Shift + Left Click` spawns an orb) |
| **Right Click** | Detonate objects near cursor with screen-shake |
| **`G`** | Toggle Top-Down vs. Side-Scroller Gravity mode |
| **`TAB`** | Toggle Live Telemetry & 16-Color Palette Inspector |
| **`R`** | Reset sandbox state |
| **`ESC`** | Quit |
