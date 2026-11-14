# PromptCraft Final Round — Participant Rules & Starter Guide

Welcome to the **PromptCraft Final Round**! All 8 finalist teams are starting from the exact same incomplete seed repository: **PIXELBOX** — a 16-color, 8-bit micro-engine built on [Pyxel](https://github.com/kitao/pyxel) ([User Guide](https://kitao.github.io/pyxel/web/user-guide/)).

You have **60 minutes** to vibe-code and prompt your way from this unfinished sandbox into a **complete, original, and polished project**.

---

## 1. Quickstart (macOS, Windows & Linux)

Make sure Python 3.8+ is installed, then run the following inside the `pixelbox_starter` folder:

```bash
# 1. Install Pyxel (pre-built wheels for Mac, Windows, and Linux)
pip install -r requirements.txt

# 2. Launch the starter sandbox
python main.py
```
*(Alternative: `pyxel run main.py`)*

---

## 2. What Is Already in Your Starter Codebase?

Right now, the project is an **unfinished engine** with no win condition, no enemies, and no domain theme:

| File | What It Contains |
| :--- | :--- |
| `main.py` | Main 30 FPS loop (`update` & `draw`), keyboard/mouse input, Top-Down vs. Side-Scroller gravity toggle (`G`), and a telemetry/palette overlay (`TAB`). |
| `engine.py` | Reusable primitives: `Entity` (with AABB collision), `ParticleSystem`, `FloatingTextManager`, and `Camera` (screen-shake + flash). |
| `assets.py` | Procedural 8×8 hex-string sprites (`"00cccc00"`) and chiptune sound effects (`"c2e2g2c3"`). |

### Starter Controls
- **Arrow Keys / WASD:** Move (`SPACE` jumps in Gravity mode or emits a pulse in Top-Down mode)
- **Left Click (`+ Shift`):** Spawn a Crate (or Energy Orb) at cursor
- **Right Click:** Detonate nearby objects with screen-shake
- **`G` Key:** Toggle **Top-Down** vs. **Gravity** physics
- **`TAB` Key:** Toggle Telemetry & 16-Color Palette Inspector
- **`R` Key:** Reset state | **`ESC`:** Quit

---

## 3. Rules of the 90-Minute Challenge

1. **Same Starting Line:** All 8 teams begin from this exact `pixelbox_starter` codebase.
2. **Stay Inside the PixelBox Stack:**
   - Your final project must run via `python main.py` using [Pyxel](https://pypi.org/project/pyxel/) on a standard desktop machine (16-color palette, pixel canvas, and Pyxel audio).
   - Python standard-library modules (`math`, `random`, `json`, `dataclasses`, etc.) are allowed.
   - Do **not** replace Pyxel with a web app, React, Tkinter, Pygame, or another engine.
3. **Open Creative Direction:** Transform this seed into any complete, original project you want—a game, interactive tool, simulation, or creative experience.

---

## 4. Final Deliverables (Due at 90 Minutes)

At the end of the 90 minutes, every team must submit:

1. **GitHub Repository Link** containing your complete, runnable codebase.
2. **Public Video Demo Link** (e.g., YouTube Unlisted, Loom, or public Google Drive link) showing your running application in action.
3. **A Complete `README.md` in Your GitHub Repo** that includes:
   - **Project Overview:** A brief explanation of what you built, how to run/use it, and **screenshots** of the app.
   - **PromptCraft Section:** An explanation of the prompts you used, how you guided your AI through the stack, and what worked (or didn't work) for you.

---

## 5. Judging Criteria (100 Points)

- **Completeness & Polish (30 pts):** Feels like a finished project with clear start/end states, responsive controls, and zero crashes.
- **PromptCraft & README Reflection (25 pts):** Quality and clarity of the prompts documented in your `README.md` and how effectively you used AI to build inside Pyxel's constraints.
- **Creative Divergence (25 pts):** How original and unexpected your final project is compared to the starter seed.
- **Retro Craft & Feel (20 pts):** Effective use of custom sprites, sound, particles, screen-shake, and the 16-color palette.
