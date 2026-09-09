# app/input/injector.py

import time

from pynput.keyboard import Controller


class TextInjector:
    """
    Types text into the currently active application.
    """

    def __init__(self, typing_interval=0.005):
        self.keyboard = Controller()
        self.typing_interval = typing_interval

    def type_text(self, text: str) -> None:
        """
        Type text at the current cursor position.
        """

        if not text:
            return

        for char in text:
            self.keyboard.type(char)

            if self.typing_interval > 0:
                time.sleep(self.typing_interval)

    def type_with_delay(
        self,
        text: str,
        delay=0.1,
    ) -> None:
        """
        Wait briefly, then type the text.
        """

        if not text:
            return

        time.sleep(delay)
        self.type_text(text)


_default_injector = None


def get_injector() -> TextInjector:
    global _default_injector

    if _default_injector is None:
        _default_injector = TextInjector()

    return _default_injector


def inject_text(text: str) -> None:
    """
    Type text into the current active cursor.
    """

    get_injector().type_text(text)