from types import SimpleNamespace

from mlx_forge.backends.stt import transcribe


def test_transcribe_returns_plain_text_from_result_object():
    def fake_generate_transcription(*, model, audio):
        assert model == "test-model"
        assert audio == "short.wav"
        return SimpleNamespace(text="plain transcript")

    assert (
        transcribe(
            "short.wav",
            model="test-model",
            generate_transcription=fake_generate_transcription,
        )
        == "plain transcript"
    )
