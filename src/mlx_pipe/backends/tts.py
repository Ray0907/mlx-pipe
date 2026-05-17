from __future__ import annotations

import io
import wave
from typing import Any, Callable, Iterable


def synthesize(
    text: str,
    *,
    model: str,
    voice: str = "af_heart",
    speed: float = 1.0,
    lang_code: str = "en",
    max_tokens: int = 1200,
    sample_rate: int = 24000,
    loader: Callable[[str], Any] | None = None,
) -> bytes:
    if loader is None:
        from mlx_audio.tts.utils import load

        loader = load

    tts_model = loader(model)
    chunks = list(
        _iter_results(
            tts_model.generate(
                text=text,
                voice=voice,
                speed=speed,
                lang_code=lang_code,
                max_tokens=max_tokens,
                verbose=False,
            )
        )
    )
    samples: list[float] = []
    for chunk in chunks:
        audio = getattr(chunk, "audio", chunk)
        sample_rate = int(getattr(chunk, "sample_rate", sample_rate))
        samples.extend(_flatten_audio(audio))

    return _wav_bytes(samples, sample_rate=sample_rate)


def _iter_results(results: Any) -> Iterable[Any]:
    if isinstance(results, (bytes, bytearray)):
        return [results]
    try:
        return iter(results)
    except TypeError:
        return [results]


def _flatten_audio(audio: Any) -> list[float]:
    if isinstance(audio, (bytes, bytearray)):
        return _pcm16_bytes_to_float_list(bytes(audio))
    if hasattr(audio, "tolist"):
        audio = audio.tolist()
    if isinstance(audio, (int, float)):
        return [float(audio)]

    flattened: list[float] = []
    for item in audio:
        if isinstance(item, list):
            flattened.extend(float(value) for value in item)
        else:
            flattened.append(float(item))
    return flattened


def _pcm16_bytes_to_float_list(audio: bytes) -> list[float]:
    values = []
    for index in range(0, len(audio), 2):
        sample = int.from_bytes(audio[index : index + 2], "little", signed=True)
        values.append(sample / 32768.0)
    return values


def _wav_bytes(samples: list[float], *, sample_rate: int) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(b"".join(_float_to_pcm16(sample) for sample in samples))
    return buffer.getvalue()


def _float_to_pcm16(sample: float) -> bytes:
    clipped = max(-1.0, min(1.0, sample))
    value = int(clipped * 32767)
    return value.to_bytes(2, "little", signed=True)
