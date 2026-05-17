from __future__ import annotations

import argparse
import sys

from mlx_forge.hub import list_models


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("list", help="List downloaded Hugging Face models")
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    for model in list_models():
        print(model, file=sys.stdout)
    return 0
