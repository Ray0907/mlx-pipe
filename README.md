# mlx-forge

Unix-style CLI wrappers for MLX speech and language models.

`mlx-forge` keeps stdout pipe-friendly:

- `stt` and `llm` write plain text to stdout.
- `tts` writes WAV bytes to stdout, or to `--out`.
- progress, model loading, and warnings go to stderr.
- `--json` is available when structured output is needed.

## Install

This project uses `uv`.

```bash
uv sync
uv run mlx-forge --help
```

Python is pinned to `>=3.11,<3.13` because the MLX audio stack is not yet stable
on Python 3.13.

## Quick Start

Run a local LLM:

```bash
uv run mlx-forge llm "Say hello in one short sentence" \
  --model mlx-community/gemma-3-1b-it-4bit
```

Transcribe audio:

```bash
uv run mlx-forge stt /tmp/asr.wav \
  --model RayyTien/Breeze-ASR-26-mlx-4bit
```

Generate speech:

```bash
uv run mlx-forge tts "Hello from Voxtral." \
  --model mlx-community/Voxtral-4B-TTS-2603-mlx-4bit \
  --voice casual_male \
  --out /tmp/voxtral.wav

file /tmp/voxtral.wav
```

Expected file output:

```text
RIFF (little-endian) data, WAVE audio, Microsoft PCM, 16 bit, mono 24000 Hz
```

## Pipe Composition

Transcribe speech, then send the transcript to an LLM:

```bash
uv run mlx-forge stt /tmp/asr.wav \
  --model RayyTien/Breeze-ASR-26-mlx-4bit \
| uv run mlx-forge llm "translate to Chinese" \
  --model mlx-community/gemma-3-1b-it-4bit
```

Generate text, then synthesize it:

```bash
uv run mlx-forge llm "explain MLX in one sentence" \
  --model mlx-community/gemma-3-1b-it-4bit \
| uv run mlx-forge tts \
  --model mlx-community/Voxtral-4B-TTS-2603-mlx-4bit \
  --voice casual_male \
  --out /tmp/mlx.wav
```

When stdin is piped into `llm`, the positional prompt is treated as the
instruction:

```text
{instruction}:

{stdin text}
```

## Logprobs

Use `--json --logprobs` to include generated token metadata. Use
`--top-logprobs N` to include the top N alternatives for each generated token.

```bash
uv run mlx-forge llm "Say hello" \
  --model mlx-community/gemma-3-1b-it-4bit \
  --json \
  --logprobs \
  --top-logprobs 5 \
  --max-tokens 8
```

Output shape:

```json
{
  "text": "Hello there! How can I help you",
  "meta": {"model": "mlx-community/gemma-3-1b-it-4bit"},
  "tokens": [
    {
      "token": 9259,
      "text": "Hello",
      "logprob": 0.0,
      "top_logprobs": [
        {"token": 9259, "text": "Hello", "logprob": 0.0}
      ]
    }
  ]
}
```

## Config

Model resolution priority is:

1. explicit `--model`
2. user config
3. built-in defaults

Set defaults:

```bash
uv run mlx-forge config set llm.default mlx-community/gemma-3-1b-it-4bit
uv run mlx-forge config set stt.default RayyTien/Breeze-ASR-26-mlx-4bit
uv run mlx-forge config set tts.default mlx-community/Voxtral-4B-TTS-2603-mlx-4bit
```

Read config:

```bash
uv run mlx-forge config get llm.default
uv run mlx-forge config list
```

By default config is stored at:

```text
~/.config/mlx-forge/config.json
```

For tests or isolated runs, override it:

```bash
MLX_FORGE_CONFIG_HOME=$(mktemp -d) uv run mlx-forge config list
```

## Model Management

Download a model:

```bash
uv run mlx-forge pull mlx-community/gemma-3-1b-it-4bit
```

List cached Hugging Face models:

```bash
uv run mlx-forge list
```

Remove cached models:

```bash
uv run mlx-forge remove mlx-community/gemma-3-1b-it-4bit
```

## Suggested Models

LLM:

```text
mlx-community/gemma-3-1b-it-4bit
```

ASR:

```text
RayyTien/Breeze-ASR-26-mlx-4bit
```

`Breeze-ASR-26` is intended for Taiwanese Hokkien / Taigi audio with Mandarin
Chinese character output. For English test audio, use an English Whisper model
instead.

TTS:

```text
mlx-community/Voxtral-4B-TTS-2603-mlx-4bit
```

Voxtral requires `tiktoken`, which is included in this package's dependencies.

## Development

Run the local checks:

```bash
uv sync
uv run pytest
uv run ruff check .
```

Run CLI smoke checks without downloading models:

```bash
uv run mlx-forge --help
uv run mlx-forge llm --help
uv run mlx-forge stt --help
uv run mlx-forge tts --help
```

Run a config smoke check:

```bash
tmpdir=$(mktemp -d)
MLX_FORGE_CONFIG_HOME=$tmpdir uv run mlx-forge config set llm.default local-llm
MLX_FORGE_CONFIG_HOME=$tmpdir uv run mlx-forge config get llm.default
MLX_FORGE_CONFIG_HOME=$tmpdir uv run mlx-forge config list
```

## CI

The GitHub Actions workflow runs on a macOS arm64 hosted runner because MLX is
Apple Silicon oriented. It verifies:

- locked dependency resolution
- unit tests
- ruff lint
- CLI help/config smoke checks

Full model e2e tests are intentionally manual for now because they download
large models and can make routine CI slow and expensive.
