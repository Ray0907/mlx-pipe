from __future__ import annotations

import argparse
import json
import sys
from typing import TextIO

from mlx_pipe.backends.stt import transcribe
from mlx_pipe.config import get_default_model


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("stt", help="Transcribe audio with an MLX speech model")
    parser.add_argument("audio", help="Path to an audio file")
    parser.add_argument("--model", help="Model id or local path")
    parser.add_argument("--json", action="store_true", help="Emit structured JSON")
    parser.set_defaults(func=run)


def run(args: argparse.Namespace, *, stdout: TextIO | None = None) -> int:
    stdout = stdout or sys.stdout
    model = get_default_model("stt", explicit=args.model)

    print(f"Loading stt model: {model}", file=sys.stderr)
    text = transcribe(args.audio, model=model)
    if args.json:
        print(json.dumps({"text": text, "meta": {"model": model}}, ensure_ascii=False), file=stdout)
    else:
        print(text, file=stdout)
    return 0
