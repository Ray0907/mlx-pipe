from types import SimpleNamespace

from mlx_forge.backends.llm import (
    _apply_chat_template,
    _clean_generated_text,
    generate_text_with_logprobs,
)


class TokenizingByDefaultTokenizer:
    def apply_chat_template(self, messages, add_generation_prompt, tokenize=True):
        assert messages == [{"role": "user", "content": "Say hello"}]
        assert add_generation_prompt is True
        if tokenize:
            return [2, 105, 2364]
        return "<start_of_turn>user\nSay hello<end_of_turn>\n<start_of_turn>model\n"


def test_apply_chat_template_requests_text_prompt_not_token_ids():
    assert _apply_chat_template(TokenizingByDefaultTokenizer(), "Say hello") == (
        "<start_of_turn>user\nSay hello<end_of_turn>\n<start_of_turn>model\n"
    )


def test_clean_generated_text_removes_chat_template_markers():
    assert _clean_generated_text("Hello!<end_of_turn>\n<end_of_turn>") == "Hello!"


class DecodingTokenizer(TokenizingByDefaultTokenizer):
    def decode(self, tokens):
        return {1: " Hello", 2: "Hi", 3: "there"}[tokens[0]]


def test_generate_text_with_logprobs_returns_token_metadata():
    responses = [
        SimpleNamespace(
            text=" Hello",
            token=1,
            logprobs=[-3.0, -0.25, -1.2, -2.0],
            finish_reason=None,
        )
    ]

    result = generate_text_with_logprobs(
        "Say hello",
        model="test-model",
        max_tokens=4,
        top_logprobs=2,
        loader=lambda model: ("loaded-model", DecodingTokenizer()),
        stream_generator=lambda *args, **kwargs: iter(responses),
    )

    assert result == {
        "text": "Hello",
        "tokens": [
            {
                "token": 1,
                "text": " Hello",
                "logprob": -0.25,
                "top_logprobs": [
                    {"token": 1, "text": " Hello", "logprob": -0.25},
                    {"token": 2, "text": "Hi", "logprob": -1.2},
                ],
            }
        ],
    }
