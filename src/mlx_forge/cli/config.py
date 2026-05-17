from __future__ import annotations

import argparse
import json
import sys

from mlx_forge.config import get_config_value, load_config, set_config_value


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("config", help="Read and write mlx-forge configuration")
    config_subparsers = parser.add_subparsers(dest="config_command", required=True)

    get_parser = config_subparsers.add_parser("get", help="Get a config value")
    get_parser.add_argument("key")
    get_parser.set_defaults(func=run_get)

    set_parser = config_subparsers.add_parser("set", help="Set a config value")
    set_parser.add_argument("key")
    set_parser.add_argument("value")
    set_parser.set_defaults(func=run_set)

    list_parser = config_subparsers.add_parser("list", help="List config as JSON")
    list_parser.set_defaults(func=run_list)


def run_get(args: argparse.Namespace) -> int:
    value = get_config_value(args.key)
    if value is None:
        return 1
    print(value, file=sys.stdout)
    return 0


def run_set(args: argparse.Namespace) -> int:
    set_config_value(args.key, args.value)
    return 0


def run_list(args: argparse.Namespace) -> int:
    print(json.dumps(load_config(), indent=2, sort_keys=True), file=sys.stdout)
    return 0
