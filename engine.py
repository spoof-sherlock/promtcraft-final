"""
PIXELBOX // Core Micro-Engine Primitives
========================================
Reusable building blocks for entities, AABB collisions, particles, floating combat/UI text,
and screen-shake camera feedback.

Finalists can extend, replace, or remix any class in this file to build:
  - An arcade platformer, roguelike, or twin-stick shooter
  - A physics puzzle toy or ecosystem simulation
  - A pixel-art editor, chiptune music sequencer, or cyber-pet simulator
"""

from dataclasses import dataclass, field
import math
import random
import pyxel
from assets import draw_sprite


@dataclass
class Entity:
    """Generic 2D actor with position, velocity, bounding box, and custom tags/state."""
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    w: int = 8
    h: int = 8
    sprite: str = "crate"
    tag: str = "neutral"
    flip_x: bool = False
    alive: bool = True
    hp: int = 3
    timer: int = 0
    data: dict = field(default_factory=dict)

    def update(self) -> None:
        self.x += self.vx
        self.y += self.vy
        self.timer += 1

    def draw(self, cam_x: float = 0.0, cam_y: float = 0.0) -> None:
        if self.alive:
            draw_sprite(self.sprite, self.x - cam_x, self.y - cam_y, flip_x=self.flip_x)

    def intersects(self, other: "Entity") -> bool:
        """Axis-Aligned Bounding Box (AABB) collision check."""
        return (
            self.alive
            and other.alive
            and self.x < other.x + other.w
            and self.x + self.w > other.x
            and self.y < other.y + other.h
            and self.y + self.h > other.y
        )

    def center(self) -> tuple[float, float]:
        return (self.x + self.w / 2.0, self.y + self.h / 2.0)


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    color: int
    life: int
    max_life: int
    size: int = 2


class ParticleSystem:
    """Lightweight particle emitter for explosions, trails, sparks, and weather."""

    def __init__(self) -> None:
        self.particles: list[Particle] = []

    def burst(
        self,
        x: float,
        y: float,
        count: int = 12,
        colors: list[int] | None = None,
        speed: float = 1.8,
        life: int = 18,
    ) -> None:
        palette = colors or [7, 9, 10, 12]
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            mag = random.uniform(0.3, speed)
            self.particles.append(
                Particle(
                    x=x,
                    y=y,
                    vx=math.cos(angle) * mag,
                    vy=math.sin(angle) * mag,
                    color=random.choice(palette),
                    life=random.randint(max(4, life // 2), life),
                    max_life=life,
                    size=random.choice([1, 2]),
                )
            )

    def update(self, gravity: float = 0.04) -> None:
        alive_list: list[Particle] = []
        for p in self.particles:
            p.x += p.vx
            p.y += p.vy
            p.vy += gravity
            p.life -= 1
            if p.life > 0:
                alive_list.append(p)
        self.particles = alive_list

    def draw(self, cam_x: float = 0.0, cam_y: float = 0.0) -> None:
        for p in self.particles:
            r = p.size if p.life > p.max_life // 3 else 1
            pyxel.rect(int(p.x - cam_x), int(p.y - cam_y), r, r, p.color)


@dataclass
class FloatingLabel:
    text: str
    x: float
    y: float
    color: int = 7
    life: int = 24


class FloatingTextManager:
    """Renders rising pixel text popups (e.g., '+10', 'COMBO!', 'SPAWN')."""

    def __init__(self) -> None:
        self.labels: list[FloatingLabel] = []

    def spawn(self, text: str, x: float, y: float, color: int = 10, life: int = 24) -> None:
        self.labels.append(FloatingLabel(text=text, x=x, y=y, color=color, life=life))

    def update(self) -> None:
        next_labels: list[FloatingLabel] = []
        for lbl in self.labels:
            lbl.y -= 0.4
            lbl.life -= 1
            if lbl.life > 0:
                next_labels.append(lbl)
        self.labels = next_labels

    def draw(self, cam_x: float = 0.0, cam_y: float = 0.0) -> None:
        for lbl in self.labels:
            # Draw 1px shadow for legibility
            pyxel.text(int(lbl.x - cam_x) + 1, int(lbl.y - cam_y) + 1, lbl.text, 0)
            pyxel.text(int(lbl.x - cam_x), int(lbl.y - cam_y), lbl.text, lbl.color)


class Camera:
    """Handles viewport offset, screen shake, and flash effects."""

    def __init__(self) -> None:
        self.x: float = 0.0
        self.y: float = 0.0
        self.shake_frames: int = 0
        self.shake_intensity: float = 0.0
        self.flash_frames: int = 0
        self.flash_color: int = 7

    def shake(self, frames: int = 6, intensity: float = 2.0) -> None:
        self.shake_frames = max(self.shake_frames, frames)
        self.shake_intensity = max(self.shake_intensity, intensity)

    def flash(self, frames: int = 3, color: int = 7) -> None:
        self.flash_frames = frames
        self.flash_color = color

    def get_offset(self) -> tuple[float, float]:
        if self.shake_frames > 0:
            ox = random.uniform(-self.shake_intensity, self.shake_intensity)
            oy = random.uniform(-self.shake_intensity, self.shake_intensity)
            return (self.x + ox, self.y + oy)
        return (self.x, self.y)

    def update(self) -> None:
        if self.shake_frames > 0:
            self.shake_frames -= 1
            if self.shake_frames == 0:
                self.shake_intensity = 0.0
        if self.flash_frames > 0:
            self.flash_frames -= 1
