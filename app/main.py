import sys
import threading
from collections import deque

import numpy as np

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QApplication

from app.audio.stream_recorder import StreamingRecorder
from app.config.settings import CHANNELS, SAMPLE_RATE, get_audio_device
from app.gui.dictionary_window import DictionaryWindow
from app.gui.microphone_window import MicrophoneWindow
from app.input.injector import TextInjector
from app.speech.hybrid_recognizer import get_recognizer
from app.speech.vad import SpeechActivityDetector
from app.transliteration.converter import BanglishConverter


# Audio kept from BEFORE the VAD says "speech started".
# Without this the first consonant is cut off
# ("চামচ" was heard as "জামচ").
PRE_ROLL_SECONDS = 0.5

MIN_UTTERANCE_SECONDS = 0.4
MAX_UTTERANCE_SECONDS = 25.0


class VoiceWorker(QObject):
    status = Signal(str)
    unknown_words = Signal(list)
    error = Signal(str)
    finished = Signal()

    def __init__(self, device=None):
        super().__init__()

        self.running = False
        self.stop_requested = threading.Event()

        if device is None:
            device = get_audio_device()

        self.device = device

        self.recorder = None
        self.vad = None
        self.recognizer = None
        self.converter = None
        self.injector = None

    @Slot()
    def run(self):
        if self.running:
            return

        self.stop_requested.clear()
        self.running = True

        speech_buffer = []

        try:
            if self.stop_requested.is_set():
                return

            self.status.emit("🧠 Loading voice engine...")

            self.vad = SpeechActivityDetector()

            if self.stop_requested.is_set():
                return

            # Loaded once, reused on every Start Listening.
            self.recognizer = get_recognizer()

            if self.stop_requested.is_set():
                return

            self.converter = BanglishConverter()
            self.injector = TextInjector(typing_interval=0.005)

            self.recorder = StreamingRecorder(
                sample_rate=SAMPLE_RATE,
                channels=CHANNELS,
                device=self.device,
            )

            if self.stop_requested.is_set():
                return

            self.recorder.start()

            self.status.emit("🔴 LISTENING... Speak now")

            pre_roll = deque()
            pre_roll_samples = 0
            max_pre_roll = int(PRE_ROLL_SECONDS * SAMPLE_RATE)
            max_samples = int(MAX_UTTERANCE_SECONDS * SAMPLE_RATE)
            buffered_samples = 0

            while self.running and not self.stop_requested.is_set():

                chunk = self.recorder.get_chunk(timeout=0.5)

                if chunk is None:
                    continue

                if not self.running or self.stop_requested.is_set():
                    break

                event = self.vad.process(chunk)

                if event == "start":
                    # Start the utterance with the audio just before it.
                    speech_buffer = list(pre_roll)
                    buffered_samples = pre_roll_samples

                if self.vad.in_speech or event == "end":
                    speech_buffer.append(chunk)
                    buffered_samples += len(chunk)

                # Rolling pre-roll window.
                pre_roll.append(chunk)
                pre_roll_samples += len(chunk)

                while pre_roll and pre_roll_samples - len(pre_roll[0]) >= max_pre_roll:
                    pre_roll_samples -= len(pre_roll.popleft())

                # Very long speech: force a cut (Whisper limit is 30 s).
                if self.vad.in_speech and buffered_samples >= max_samples:
                    event = "end"

                if event == "end":

                    if not speech_buffer:
                        self.vad.reset()
                        continue

                    if not self.running or self.stop_requested.is_set():
                        speech_buffer = []
                        self.vad.reset()
                        break

                    audio = np.concatenate(speech_buffer)
                    speech_buffer = []
                    buffered_samples = 0

                    # Don't let the tail of this sentence leak into the next.
                    pre_roll.clear()
                    pre_roll_samples = 0

                    if len(audio) < MIN_UTTERANCE_SECONDS * SAMPLE_RATE:
                        self.vad.reset()
                        continue

                    bangla_text = self.recognizer.transcribe(
                        audio,
                        sample_rate=SAMPLE_RATE,
                    )

                    if not self.running or self.stop_requested.is_set():
                        speech_buffer = []
                        self.vad.reset()
                        break

                    if not bangla_text:
                        speech_buffer = []
                        self.vad.reset()
                        continue

                    print(f"🇧🇩 ASR: {bangla_text}")

                    banglish, unknown = (
                        self.converter.convert_with_unknowns(
                            bangla_text
                        )
                    )

                    if not self.running or self.stop_requested.is_set():
                        speech_buffer = []
                        self.vad.reset()
                        break

                    print(f"🔤 OUT: {banglish}")

                    if unknown:
                        self.unknown_words.emit(unknown)

                    if (
                        banglish
                        and self.running
                        and not self.stop_requested.is_set()
                    ):
                        self.injector.type_text(
                            banglish + " "
                        )

                    speech_buffer = []
                    self.vad.reset()

            self.status.emit("⚪ LISTENING STOPPED")

        except Exception as exc:
            if not self.stop_requested.is_set():
                print(f"❌ Voice worker error: {exc}")
                self.error.emit(str(exc))

        finally:
            self.running = False

            if self.recorder is not None:
                try:
                    self.recorder.stop()
                except Exception:
                    pass

            if self.vad is not None:
                try:
                    self.vad.reset()
                except Exception:
                    pass

            self.finished.emit()

    def stop(self):
        self.stop_requested.set()
        self.running = False

        if self.recorder is not None:
            try:
                self.recorder.stop()
            except Exception:
                pass


class VoiceApp(QObject):
    """
    QObject, so worker signals (emitted from a background thread)
    are delivered on the GUI thread. Touching widgets from another
    thread can crash Qt randomly.
    """

    def __init__(self, app):
        super().__init__()

        self.app = app

        self.microphone_window = None
        self.dictionary_window = None

        self.worker = None
        self.thread = None

        self.show_microphone_selection()

    def show_microphone_selection(self):
        self.microphone_window = MicrophoneWindow()

        self.microphone_window.start_requested.connect(
            self.start_voice
        )

        self.microphone_window.show()

    @Slot(int)
    def start_voice(self, device):
        if self.worker is not None and self.worker.running:
            return

        print("🎙️ Starting Voice")

        if self.microphone_window:
            self.microphone_window.close()
            self.microphone_window.deleteLater()
            self.microphone_window = None

        if self.dictionary_window is None:
            self.dictionary_window = DictionaryWindow()

            self.dictionary_window.start_listening_requested.connect(
                self.start_listening
            )

            self.dictionary_window.stop_listening_requested.connect(
                self.stop_listening
            )

            self.dictionary_window.window_closed.connect(
                self.stop_voice
            )

            self.dictionary_window.show()

        self.start_listening()

    @Slot()
    def start_listening(self):
        if self.worker is not None:
            if self.worker.running:
                return

            if self.thread is not None and self.thread.is_alive():
                # Previous run is still finishing a transcription.
                if self.dictionary_window:
                    self.dictionary_window.set_listening_state(False)
                    self.dictionary_window.status_label.setText(
                        "⏳ Finishing last sentence... try again in a moment"
                    )
                return

        device = get_audio_device()

        self.worker = VoiceWorker(device=device)

        self.worker.status.connect(
            self.handle_status
        )

        self.worker.unknown_words.connect(
            self.handle_unknown_words
        )

        self.worker.error.connect(
            self.handle_error
        )

        self.worker.finished.connect(
            self.handle_finished
        )

        self.thread = threading.Thread(
            target=self.worker.run,
            daemon=True,
        )

        self.thread.start()

        if self.dictionary_window:
            self.dictionary_window.set_listening_state(True)

    @Slot()
    def stop_listening(self):
        if self.worker is None:
            return

        self.worker.stop()

        if self.dictionary_window:
            self.dictionary_window.set_listening_state(False)
            self.dictionary_window.status_label.setText(
                "⚪ LISTENING STOPPED"
            )

    @Slot()
    def stop_voice(self):
        if self.worker is not None:
            self.worker.stop()

    @Slot(str)
    def handle_status(self, message):
        if self.dictionary_window:
            self.dictionary_window.status_label.setText(
                message
            )

    @Slot(list)
    def handle_unknown_words(self, words):
        if self.dictionary_window:
            self.dictionary_window.refresh_unknown_words()

    @Slot(str)
    def handle_error(self, message):
        print(f"❌ Voice error: {message}")

        if self.dictionary_window:
            self.dictionary_window.status_label.setText(
                f"❌ Error: {message}"
            )
            self.dictionary_window.set_listening_state(False)

    @Slot()
    def handle_finished(self):
        if self.dictionary_window:
            self.dictionary_window.set_listening_state(False)

            if self.dictionary_window.isVisible():
                self.dictionary_window.status_label.setText(
                    "⚪ LISTENING STOPPED"
                )

        self.worker = None
        self.thread = None

    def run(self):
        return self.app.exec()


def main():
    app = QApplication(sys.argv)
    voice_app = VoiceApp(app)
    sys.exit(voice_app.run())


if __name__ == "__main__":
    main()