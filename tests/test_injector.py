from unittest.mock import MagicMock, call

from app.input.injector import TextInjector


def test_injector_types_text():
    injector = TextInjector(
        typing_interval=0
    )

    injector.keyboard = MagicMock()

    injector.type_text(
        "ami"
    )

    expected_calls = [
        call("a"),
        call("m"),
        call("i"),
    ]

    assert injector.keyboard.type.call_args_list == expected_calls


def test_empty_text_is_ignored():
    injector = TextInjector()

    injector.keyboard = MagicMock()

    injector.type_text("")

    injector.keyboard.type.assert_not_called()


def test_none_text_is_ignored():
    injector = TextInjector()

    injector.keyboard = MagicMock()

    injector.type_text(None)

    injector.keyboard.type.assert_not_called()