#!/usr/bin/env python3
"""Offline ESP demo: fake entities + ViewMatrix + W2S. No game process required.

    python esp_demo.py --demo
    python esp_demo.py --demo --frames 3 --no-gui
"""
from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple

Vec3 = Tuple[float, float, float]
Mat4 = Sequence[Sequence[float]]


@dataclass
class Entity:
    name: str
    x: float
    y: float
    z: float
    health: int
    team: int


def pinhole_matrix(width: int, height: int, fov_deg: float = 70.0) -> List[List[float]]:
    """Camera at origin looking +Z. clip_w = z, so points with z <= 0 are behind the camera."""
    aspect = width / float(height)
    f = 1.0 / math.tan(math.radians(fov_deg) / 2.0)
    return [
        [f / aspect, 0.0, 0.0, 0.0],
        [0.0, f, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
    ]


def w2s(world: Vec3, matrix: Mat4, width: int, height: int) -> Optional[Tuple[int, int, float]]:
    """world → clip → NDC → screen. None if behind camera (w <= 0)."""
    x, y, z = world
    clip_x = matrix[0][0] * x + matrix[0][1] * y + matrix[0][2] * z + matrix[0][3]
    clip_y = matrix[1][0] * x + matrix[1][1] * y + matrix[1][2] * z + matrix[1][3]
    clip_w = matrix[3][0] * x + matrix[3][1] * y + matrix[3][2] * z + matrix[3][3]
    if clip_w <= 0.01:
        return None
    ndc_x = clip_x / clip_w
    ndc_y = clip_y / clip_w
    sx = int((ndc_x + 1.0) * 0.5 * width)
    sy = int((1.0 - ndc_y) * 0.5 * height)
    return sx, sy, clip_w


def demo_entities() -> List[Entity]:
    return [
        Entity("alpha", -3.0, 0.0, 8.0, 100, 1),
        Entity("bravo", 4.0, 0.0, 12.0, 75, 2),
        Entity("charlie", 0.0, 0.0, 18.0, 30, 2),
        Entity("behind", 0.0, 0.0, -30.0, 100, 1),
    ]


def project_all(
    entities: Iterable[Entity], matrix: Mat4, width: int, height: int
) -> List[Tuple[Entity, Tuple[int, int, float]]]:
    out: List[Tuple[Entity, Tuple[int, int, float]]] = []
    for ent in entities:
        hit = w2s((ent.x, ent.y, ent.z), matrix, width, height)
        if hit is None:
            continue
        out.append((ent, hit))
    return out


def render_ascii(hits: List[Tuple[Entity, Tuple[int, int, float]]], width: int, height: int) -> str:
    grid = [["."] * 40 for _ in range(12)]
    for ent, (sx, sy, _) in hits:
        col = max(0, min(39, int(sx / width * 40)))
        row = max(0, min(11, int(sy / height * 12)))
        grid[row][col] = ent.name[0].upper()
    return "\n".join("".join(r) for r in grid)


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Offline ESP demo")
    p.add_argument("--demo", action="store_true", default=True, help="use fake entities (default)")
    p.add_argument("--width", type=int, default=1920)
    p.add_argument("--height", type=int, default=1080)
    p.add_argument("--frames", type=int, default=1)
    p.add_argument("--no-gui", action="store_true", help="never open a window")
    args = p.parse_args(argv)

    matrix = pinhole_matrix(args.width, args.height)
    ents = demo_entities()
    hits = project_all(ents, matrix, args.width, args.height)
    print(f"entities={len(ents)} projected={len(hits)} skipped={len(ents) - len(hits)}")
    for ent, (sx, sy, w) in hits:
        print(f"  {ent.name:8s} team={ent.team} hp={ent.health:3d} screen=({sx:4d},{sy:4d}) w={w:.2f}")
    print("--- ascii ---")
    print(render_ascii(hits, args.width, args.height))
    if not args.no_gui:
        try:
            import tkinter  # noqa: F401
        except Exception as exc:
            print(f"gui unavailable: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
