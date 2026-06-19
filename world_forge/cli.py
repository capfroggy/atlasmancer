"""Command-line interface for world-forge."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .generator import generate_world


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="world-forge",
        description="Generate tiny deterministic ASCII worlds.",
    )
    parser.add_argument("--seed", help="Seed text for deterministic worlds.")
    parser.add_argument("--width", type=int, default=72, help="Map width, from 24 to 140.")
    parser.add_argument("--height", type=int, default=28, help="Map height, from 12 to 60.")
    parser.add_argument(
        "--landmarks",
        type=int,
        default=9,
        help="Number of named places to add, from 0 to 30.",
    )
    parser.add_argument(
        "--format",
        choices=("plain", "ansi", "markdown", "json"),
        default="plain",
        help="Output format.",
    )
    parser.add_argument("--output", type=Path, help="Write output to a file.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    world = generate_world(
        seed=args.seed,
        width=args.width,
        height=args.height,
        landmark_count=args.landmarks,
    )

    if args.format == "json":
        output = world.to_json()
    elif args.format == "markdown":
        output = world.to_markdown()
    elif args.format == "ansi":
        output = world.render_ansi()
    else:
        output = world.render_plain()

    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        sys.stdout.write(output + "\n")

    return 0
