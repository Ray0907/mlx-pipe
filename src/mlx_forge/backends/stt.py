from __future__ import annotations

from typing import Any, Callable


def _load_generate_transcription() -> Callable[..., Any]:
    from mlx_audio.stt.generate import generate_transcription

    return generate_transcription


def transcribe(
    audio_path: str,
    *,
    model: str,
    generate_transcription: Callable[..., Any] | None = None,
) -> str:
    generator = generate_transcription or _load_generate_transcription()
    result = generator(model=model, audio=audio_path)

    if isinstance(result, str):
        return result
    if isinstance(result, dict) and "text" in result:
        return str(result["text"])
    if hasattr(result, "text"):
        return str(result.text)

    raise TypeError("STT backend did not return a text result")
