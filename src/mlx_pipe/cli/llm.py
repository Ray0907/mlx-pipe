from __future__ import annotations

import argparse
import json
import sys
from typing import TextIO

from mlx_pipe.backends.llm import generate_text, generate_text_with_logprobs
from mlx_pipe.config import get_default_model


def build_prompt(prompt: str, stdin_text: str) -> str:
    stdin_text = stdin_text.strip()
    if not stdin_text:
        return prompt
    return f"{prompt}:\n\n{stdin_text}"


def register_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("llm", help="Generate text with an MLX language model")
    parser.add_argument("prompt", help="Prompt or instruction")
    parser.add_argument("--model", help="Model id or local path")
    parser.add_argument("--max-tokens", type=int, default=512)
    parser.add_argument("--json", action="store_true", help="Emit structured JSON")
    parser.add_argument("--logprobs", action="store_true", help="Include generated token logprobs")
    parser.add_argument(
        "--top-logprobs",
        type=int,
        default=0,
        help="Include top N token logprobs for each generated token",
    )
    parser.set_defaults(func=run)


def run(args: argparse.Namespace, *, stdin: TextIO | None = None, stdout: TextIO | None = None) -> int:
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    stdin_text = "" if stdin.isatty() else stdin.read()
    prompt = build_prompt(args.prompt, stdin_text)
    model = get_default_model("llm", explicit=args.model)

    print(f"Loading llm model: {model}", file=sys.stderr)
    if args.logprobs or args.top_logprobs:
        if not args.json:
            raise SystemExit("--logprobs and --top-logprobs require --json")
        result = generate_text_with_logprobs(
            prompt,
            model=model,
            max_tokens=args.max_tokens,
            top_logprobs=args.top_logprobs,
        )
        print(
            json.dumps(
                {"text": result["text"], "meta": {"model": model}, "tokens": result["tokens"]},
                ensure_ascii=False,
            ),
            file=stdout,
        )
        return 0

    text = generate_text(prompt, model=model, max_tokens=args.max_tokens)
    if args.json:
        print(json.dumps({"text": text, "meta": {"model": model}}, ensure_ascii=False), file=stdout)
    else:
        print(text, file=stdout)
    return 0
