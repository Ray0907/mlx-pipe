from mlx_forge.cli.main import build_parser


def test_parser_registers_core_commands():
    parser = build_parser()

    assert parser.parse_args(["stt", "short.wav"]).command == "stt"
    assert parser.parse_args(["llm", "hello"]).command == "llm"
    assert parser.parse_args(["tts", "hello"]).command == "tts"
    assert parser.parse_args(["config", "list"]).command == "config"
