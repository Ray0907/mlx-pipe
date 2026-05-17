from types import SimpleNamespace

from mlx_pipe.backends.tts import synthesize


class FakeTtsModel:
    def generate(self, **kwargs):
        text = kwargs["text"]
        voice = kwargs["voice"]
        assert text == "hello"
        assert voice == "casual_male"
        assert kwargs["speed"] == 1.1
        assert kwargs["lang_code"] == "en"
        return [SimpleNamespace(audio=[0.0, 0.5, -0.5], sample_rate=16000)]


def test_synthesize_returns_wav_bytes():
    wav = synthesize(
        "hello",
        model="test-model",
        voice="casual_male",
        speed=1.1,
        lang_code="en",
        loader=lambda model: FakeTtsModel(),
    )

    assert wav.startswith(b"RIFF")
    assert b"WAVE" in wav[:16]
