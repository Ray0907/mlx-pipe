from __future__ import annotations

import argparse

from mlx_forge.hub import remove_models


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("remove", help="Remove downloaded Hugging Face models")
    parser.add_argument("models", nargs="+")
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    remove_models(args.models)
    return 0
