"""Command-line interface for Atlasmancer."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .campaign_loader import CampaignLoadError, load_campaign, localize_world
from .generator import generate_world
from .i18n import DEFAULT_LOCALE, UnsupportedLocaleError, available_locales, load_locale
from .renderers.html import render_html


def build_parser(locale: str = DEFAULT_LOCALE) -> argparse.ArgumentParser:
    catalog = load_locale(locale)
    parser = argparse.ArgumentParser(
        prog="atlasmancer",
        description=catalog.t("cli.description"),
    )
    parser.add_argument("--seed", help=catalog.t("cli.flags.seed"))
    parser.add_argument("--width", type=int, default=72, help=catalog.t("cli.flags.width"))
    parser.add_argument("--height", type=int, default=28, help=catalog.t("cli.flags.height"))
    parser.add_argument(
        "--landmarks",
        type=int,
        default=9,
        help=catalog.t("cli.flags.landmarks"),
    )
    parser.add_argument(
        "--format",
        choices=("plain", "ansi", "markdown", "json", "campaign", "html", "png"),
        default="plain",
        help=f"{catalog.t('cli.flags.format')} {catalog.t('format.json_deprecated_note')}",
    )
    parser.add_argument(
        "--locale",
        default=DEFAULT_LOCALE,
        help=catalog.t("cli.flags.locale"),
    )
    parser.add_argument(
        "--audience",
        choices=("gm", "player"),
        default="gm",
        help=catalog.t("cli.flags.audience"),
    )
    parser.add_argument(
        "--tile-size",
        type=int,
        default=12,
        help=catalog.t("cli.flags.tile_size"),
    )
    parser.add_argument("--open", type=Path, help=catalog.t("cli.flags.open"))
    parser.add_argument("--output", type=Path, help=catalog.t("cli.flags.output"))
    return parser


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    requested_locale = _requested_locale(argv)
    parser_locale = requested_locale if requested_locale in available_locales() else DEFAULT_LOCALE
    parser = build_parser(parser_locale)
    args = parser.parse_args(argv)
    catalog = load_locale(parser_locale)

    try:
        load_locale(args.locale)
    except UnsupportedLocaleError:
        parser.error(
            catalog.t(
                "cli.errors.unsupported_locale",
                locale=args.locale,
                available=", ".join(available_locales()),
            )
        )

    if args.format == "campaign" and args.audience == "player" and args.output:
        parser.error(catalog.t("cli.errors.campaign_audience_player_not_allowed"))

    if args.open:
        try:
            world = localize_world(load_campaign(args.open, locale=args.locale), args.locale)
        except CampaignLoadError as error:
            parser.error(str(error))
    else:
        world = generate_world(
            seed=args.seed,
            width=args.width,
            height=args.height,
            landmark_count=args.landmarks,
            locale=args.locale,
        )

    if args.format == "png":
        if not args.output:
            parser.error(catalog.t("cli.errors.png_requires_output"))
        from .renderers.png import render_png

        try:
            render_png(world, args.output, tile_size=args.tile_size, audience=args.audience)
        except RuntimeError as error:
            parser.error(str(error))
        return 0

    if args.format == "json":
        output = world.to_json()
    elif args.format == "campaign":
        from .renderers.campaign import render_campaign

        output = render_campaign(world, audience=args.audience)
    elif args.format == "markdown":
        output = world.to_markdown(audience=args.audience)
    elif args.format == "html":
        output = render_html(world, audience=args.audience)
    elif args.format == "ansi":
        output = world.render_ansi(audience=args.audience)
    else:
        output = world.render_plain(audience=args.audience)

    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        sys.stdout.write(output + "\n")

    return 0


def _requested_locale(argv: list[str]) -> str:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--locale", default=DEFAULT_LOCALE)
    args, _ = parser.parse_known_args(argv)
    return args.locale
