import argparse
import io
import json

import mlx_forge.cli.llm as llm_cli
from mlx_forge.cli.llm import build_prompt


def test_build_prompt_uses_instruction_then_stdin_context():
    assert build_prompt("summarize as bullet points", "meeting transcript") == (
        "summarize as bullet points:\n\nmeeting transcript"
    )


def test_build_prompt_uses_prompt_alone_without_stdin_context():
    assert build_prompt("hello", "") == "hello"


def test_llm_json_logprobs_cli_emits_token_metadata(monkeypatch):
    def fake_generate_text_with_logprobs(prompt, *, model, max_tokens, top_logprobs):
        assert prompt == "Say hello"
        assert model == "test-model"
        assert max_tokens == 8
        assert top_logprobs == 2
        return {
            "text": "Hello",
            "tokens": [
                {
                    "token": 1,
                    "text": "Hello",
                    "logprob": -0.1,
                    "top_logprobs": [{"token": 1, "text": "Hello", "logprob": -0.1}],
                }
            ],
        }

    monkeypatch.setattr(llm_cli, "generate_text_with_logprobs", fake_generate_text_with_logprobs)
    args = argparse.Namespace(
        prompt="Say hello",
        model="test-model",
        max_tokens=8,
        json=True,
        logprobs=True,
        top_logprobs=2,
    )
    stdout = io.StringIO()

    assert llm_cli.run(args, stdin=io.StringIO(""), stdout=stdout) == 0

    assert json.loads(stdout.getvalue()) == {
        "text": "Hello",
        "meta": {"model": "test-model"},
        "tokens": [
            {
                "token": 1,
                "text": "Hello",
                "logprob": -0.1,
                "top_logprobs": [{"token": 1, "text": "Hello", "logprob": -0.1}],
            }
        ],
    }
