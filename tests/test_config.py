import json

from mlx_pipe.config import get_default_model, load_config, set_config_value
from mlx_pipe.registry import BUILTIN_DEFAULTS


def test_default_model_resolution_prefers_explicit_over_config_and_builtin(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"defaults": {"llm": "user-configured-model"}}),
        encoding="utf-8",
    )

    assert get_default_model("llm", explicit="explicit-model", config_path=config_path) == "explicit-model"


def test_default_model_resolution_prefers_user_config_over_builtin(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"defaults": {"llm": "user-configured-model"}}),
        encoding="utf-8",
    )

    assert get_default_model("llm", config_path=config_path) == "user-configured-model"


def test_default_model_resolution_falls_back_to_builtin(tmp_path):
    config_path = tmp_path / "missing.json"

    assert get_default_model("llm", config_path=config_path) == BUILTIN_DEFAULTS["llm"]


def test_set_config_value_creates_nested_config(tmp_path):
    config_path = tmp_path / "config.json"

    set_config_value("stt.default", "custom-stt", config_path=config_path)

    assert load_config(config_path) == {"defaults": {"stt": "custom-stt"}}
