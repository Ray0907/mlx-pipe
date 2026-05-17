from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from mlx_forge.cli import config, list, llm, pull, remove, stt, tts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mlx-forge")
    subparsers = parser.add_subparsers(dest="command", required=True)
    stt.register_parser(subparsers)
    llm.register_parser(subparsers)
    tts.register_parser(subparsers)
    pull.register_parser(subparsers)
    list.register_parser(subparsers)
    remove.register_parser(subparsers)
    config.register_parser(subparsers)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
