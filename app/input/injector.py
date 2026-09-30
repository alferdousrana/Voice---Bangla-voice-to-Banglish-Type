# app/input/injector.py

import ctypes
import time
from ctypes import wintypes

from pynput.keyboard import Controller, Key


# =========================================================
# WINDOWS API
# =========================================================

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)


CF_UNICODETEXT = 13

GMEM_MOVEABLE = 0x0002
GMEM_ZEROINIT = 0x0040


# ---------------------------------------------------------
# Clipboard API definitions
# ---------------------------------------------------------

user32.OpenClipboard.argtypes = [
    wintypes.HWND,
]

user32.OpenClipboard.restype = wintypes.BOOL


user32.CloseClipboard.argtypes = []

user32.CloseClipboard.restype = wintypes.BOOL


user32.EmptyClipboard.argtypes = []

user32.EmptyClipboard.restype = wintypes.BOOL


user32.GetClipboardData.argtypes = [
    wintypes.UINT,
]

user32.GetClipboardData.restype = wintypes.HANDLE


user32.SetClipboardData.argtypes = [
    wintypes.UINT,
    wintypes.HANDLE,
]

user32.SetClipboardData.restype = wintypes.HANDLE


kernel32.GlobalAlloc.argtypes = [
    wintypes.UINT,
    ctypes.c_size_t,
]

kernel32.GlobalAlloc.restype = wintypes.HGLOBAL


kernel32.GlobalLock.argtypes = [
    wintypes.HGLOBAL,
]

kernel32.GlobalLock.restype = ctypes.c_void_p


kernel32.GlobalUnlock.argtypes = [
    wintypes.HGLOBAL,
]

kernel32.GlobalUnlock.restype = wintypes.BOOL


kernel32.GlobalFree.argtypes = [
    wintypes.HGLOBAL,
]

kernel32.GlobalFree.restype = wintypes.HGLOBAL


# =========================================================
# TEXT INJECTOR
# =========================================================

class TextInjector:
    """
    Inject text into the currently active application.

    Windows strategy:

        Generated text
              ↓
        Windows Clipboard
              ↓
          Ctrl + V
              ↓
        Active application

    This avoids character-by-character keyboard typing.
    """

    def __init__(self, typing_interval=0.0):

        self.keyboard = Controller()

        # Kept for compatibility with the existing project.
        # Clipboard injection does not type character by character.
        self.typing_interval = typing_interval

    # =====================================================
    # CLIPBOARD
    # =====================================================

    def _open_clipboard(self):

        # Clipboard may temporarily be busy because another
        # application is accessing it.
        for _ in range(10):

            if user32.OpenClipboard(None):

                return True

            time.sleep(0.01)

        return False

    def _close_clipboard(self):

        user32.CloseClipboard()

    # =====================================================
    # GET CLIPBOARD TEXT
    # =====================================================

    def _get_clipboard_text(self):

        if not self._open_clipboard():

            return None

        try:

            handle = user32.GetClipboardData(
                CF_UNICODETEXT
            )

            if not handle:

                return None

            pointer = kernel32.GlobalLock(
                handle
            )

            if not pointer:

                return None

            try:

                return ctypes.wstring_at(
                    pointer
                )

            finally:

                kernel32.GlobalUnlock(
                    handle
                )

        except Exception as exc:

            print(
                f"⚠️ Clipboard read warning: {exc}"
            )

            return None

        finally:

            self._close_clipboard()

    # =====================================================
    # SET CLIPBOARD TEXT
    # =====================================================

    def _set_clipboard_text(self, text):

        if not self._open_clipboard():

            raise RuntimeError(
                "Could not open Windows clipboard."
            )

        memory = None

        try:

            if not user32.EmptyClipboard():

                raise RuntimeError(
                    "Could not clear Windows clipboard."
                )

            # Windows Unicode clipboard requires UTF-16LE
            # text with a terminating NULL character.
            data = (
                str(text) + "\0"
            ).encode(
                "utf-16-le"
            )

            size = len(data)

            # Explicit ctypes.c_size_t prevents the
            # previous OverflowError.
            memory = kernel32.GlobalAlloc(
                GMEM_MOVEABLE | GMEM_ZEROINIT,
                ctypes.c_size_t(size),
            )

            if not memory:

                raise RuntimeError(
                    "Could not allocate clipboard memory."
                )

            pointer = kernel32.GlobalLock(
                memory
            )

            if not pointer:

                kernel32.GlobalFree(
                    memory
                )

                memory = None

                raise RuntimeError(
                    "Could not lock clipboard memory."
                )

            try:

                ctypes.memmove(
                    pointer,
                    data,
                    size,
                )

            finally:

                kernel32.GlobalUnlock(
                    memory
                )

            result = user32.SetClipboardData(
                CF_UNICODETEXT,
                memory,
            )

            if not result:

                kernel32.GlobalFree(
                    memory
                )

                memory = None

                raise RuntimeError(
                    "Could not set clipboard data."
                )

            # IMPORTANT:
            # After successful SetClipboardData(),
            # Windows owns the memory.
            memory = None

        finally:

            self._close_clipboard()

            # Safety cleanup if ownership was not
            # transferred to Windows.
            if memory:

                try:

                    kernel32.GlobalFree(
                        memory
                    )

                except Exception:

                    pass

    # =====================================================
    # PASTE
    # =====================================================

    def _paste(self):

        # One single Ctrl+V operation.
        self.keyboard.press(
            Key.ctrl
        )

        try:

            self.keyboard.press(
                "v"
            )

            self.keyboard.release(
                "v"
            )

        finally:

            self.keyboard.release(
                Key.ctrl
            )

    # =====================================================
    # TYPE TEXT
    # =====================================================

    def type_text(self, text: str) -> None:
        """
        Inject complete text at the current cursor.

        No character-by-character typing.

        Uses:

            Clipboard → Ctrl+V
        """

        if not text:

            return

        text = str(text)

        # -------------------------------------------------
        # SAVE CURRENT CLIPBOARD
        # -------------------------------------------------

        previous_clipboard = (
            self._get_clipboard_text()
        )

        try:

            # -------------------------------------------------
            # COPY GENERATED TEXT
            # -------------------------------------------------

            self._set_clipboard_text(
                text
            )

            # Small synchronization delay.
            time.sleep(0.03)

            # -------------------------------------------------
            # SINGLE PASTE
            # -------------------------------------------------

            self._paste()

            # Give target application time to process
            # the paste before restoring clipboard.
            time.sleep(0.05)

        finally:

            # -------------------------------------------------
            # RESTORE PREVIOUS TEXT CLIPBOARD
            # -------------------------------------------------

            if previous_clipboard is not None:

                try:

                    self._set_clipboard_text(
                        previous_clipboard
                    )

                except Exception as exc:

                    print(
                        f"⚠️ Could not restore clipboard: "
                        f"{exc}"
                    )

    # =====================================================
    # TYPE WITH DELAY
    # =====================================================

    def type_with_delay(
        self,
        text: str,
        delay=0.1,
    ) -> None:
        """
        Wait briefly, then inject text.
        """

        if not text:

            return

        time.sleep(
            delay
        )

        self.type_text(
            text
        )


# =========================================================
# DEFAULT INJECTOR
# =========================================================

_default_injector = None


def get_injector() -> TextInjector:

    global _default_injector

    if _default_injector is None:

        _default_injector = TextInjector()

    return _default_injector


def inject_text(text: str) -> None:
    """
    Inject text into the current active cursor.
    """

    get_injector().type_text(
        text
    )