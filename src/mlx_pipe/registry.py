BUILTIN_DEFAULTS = {
    "stt": "mlx-community/whisper-large-v3-mlx",
    "llm": "mlx-community/gemma-3-1b-it-4bit",
    "tts": "mlx-community/kokoro-82m-mlx",
}


def known_domains() -> tuple[str, ...]:
    return tuple(BUILTIN_DEFAULTS)
