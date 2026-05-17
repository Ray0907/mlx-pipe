from __future__ import annotations

import argparse
import sys

from mlx_pipe.hub import pull_model


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("pull", help="Download a model from Hugging Face")
    parser.add_argument("model")
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    path = pull_model(args.model)
    print(str(path), file=sys.stdout)
    return 0
