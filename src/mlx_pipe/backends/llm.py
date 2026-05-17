from __future__ import annotations

from typing import Any, Callable


def generate_text(
    prompt: str,
    *,
    model: str,
    max_tokens: int = 512,
    loader: Callable[[str], tuple[object, object]] | None = None,
    generator: Callable[..., str] | None = None,
) -> str:
    if loader is None or generator is None:
        from mlx_lm import generate, load

        loader = loader or load
        generator = generator or generate

    loaded_model, tokenizer = loader(model)
    formatted_prompt = _apply_chat_template(tokenizer, prompt)
    return _clean_generated_text(
        str(
            generator(
                loaded_model,
                tokenizer,
                prompt=formatted_prompt,
                max_tokens=max_tokens,
                verbose=False,
            )
        )
    )


def generate_text_with_logprobs(
    prompt: str,
    *,
    model: str,
    max_tokens: int = 512,
    top_logprobs: int = 0,
    loader: Callable[[str], tuple[object, object]] | None = None,
    stream_generator: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    if loader is None or stream_generator is None:
        from mlx_lm import load, stream_generate

        loader = loader or load
        stream_generator = stream_generator or stream_generate

    loaded_model, tokenizer = loader(model)
    formatted_prompt = _apply_chat_template(tokenizer, prompt)
    text_parts: list[str] = []
    tokens: list[dict[str, Any]] = []

    for response in stream_generator(
        loaded_model,
        tokenizer,
        formatted_prompt,
        max_tokens=max_tokens,
    ):
        text_part = str(getattr(response, "text", ""))
        text_parts.append(text_part)

        token = getattr(response, "token", None)
        logprobs = getattr(response, "logprobs", None)
        if token is None or logprobs is None:
            continue

        token_id = int(token)
        token_info: dict[str, Any] = {
            "token": token_id,
            "text": _clean_token_text(text_part) or _decode_token(tokenizer, token_id),
            "logprob": _logprob_at(logprobs, token_id),
        }
        if top_logprobs > 0:
            token_info["top_logprobs"] = _top_logprobs(logprobs, tokenizer, top_logprobs)
        tokens.append(token_info)

    return {"text": _clean_generated_text("".join(text_parts)), "tokens": tokens}


def _apply_chat_template(tokenizer: object, prompt: str) -> str:
    apply_chat_template = getattr(tokenizer, "apply_chat_template", None)
    if not callable(apply_chat_template):
        return prompt

    messages = [{"role": "user", "content": prompt}]
    try:
        formatted = apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
    except TypeError:
        formatted = apply_chat_template(messages, add_generation_prompt=True)

    if isinstance(formatted, list):
        decode = getattr(tokenizer, "decode", None)
        if callable(decode):
            return str(decode(formatted))
    return str(formatted)


def _clean_generated_text(text: str) -> str:
    for marker in ("<end_of_turn>", "<start_of_turn>model"):
        text = text.replace(marker, "")
    return text.strip()


def _clean_token_text(text: str) -> str:
    for marker in ("<end_of_turn>", "<start_of_turn>model"):
        text = text.replace(marker, "")
    return text


def _decode_token(tokenizer: object, token: int) -> str:
    decode = getattr(tokenizer, "decode", None)
    if callable(decode):
        try:
            return str(decode([token]))
        except TypeError:
            return str(decode(token))
    return str(token)


def _logprob_at(logprobs: Any, token: int) -> float:
    return _as_float(logprobs[token])


def _top_logprobs(logprobs: Any, tokenizer: object, count: int) -> list[dict[str, Any]]:
    values = _as_list(logprobs)
    top = sorted(enumerate(values), key=lambda item: item[1], reverse=True)[:count]
    return [
        {
            "token": int(token),
            "text": _decode_token(tokenizer, int(token)),
            "logprob": _as_float(logprob),
        }
        for token, logprob in top
    ]


def _as_list(value: Any) -> list[Any]:
    if hasattr(value, "tolist"):
        return value.tolist()
    return list(value)


def _as_float(value: Any) -> float:
    if hasattr(value, "item"):
        value = value.item()
    return float(value)
