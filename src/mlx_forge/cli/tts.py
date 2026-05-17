from __future__ import annotations

import argparse
import sys

from mlx_forge.backends.tts import synthesize
from mlx_forge.config import get_default_model


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("tts", help="Generate WAV audio with an MLX speech model")
    parser.add_argument("text", nargs="?", help="Text to synthesize; stdin is used when omitted")
    parser.add_argument("--model", help="Model id or local path")
    parser.add_argument("--voice", default="af_heart")
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--lang-code", default="en")
    parser.add_argument("--max-tokens", type=int, default=1200)
    parser.add_argument("--out", help="Write WAV bytes to this path instead of stdout")
    parser.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    text = args.text
    if text is None:
        text = "" if sys.stdin.isatty() else sys.stdin.read()
    text = text.strip()
    if not text:
        raise SystemExit("tts requires text via an argument or stdin")

    model = get_default_model("tts", explicit=args.model)
    print(f"Loading tts model: {model}", file=sys.stderr)
    wav = synthesize(
        text,
        model=model,
        voice=args.voice,
        speed=args.speed,
        lang_code=args.lang_code,
        max_tokens=args.max_tokens,
    )
    if args.out:
        with open(args.out, "wb") as file:
            file.write(wav)
    else:
        sys.stdout.buffer.write(wav)
    return 0
