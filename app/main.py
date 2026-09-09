# app/main.py

import numpy as np

from app.audio.stream_recorder import StreamingRecorder
from app.speech.vad import SpeechActivityDetector
from app.speech.fast_recognizer import FastBanglaRecognizer
from app.transliteration.converter import BanglishConverter
from app.input.injector import TextInjector


SAMPLE_RATE = 16000
CHUNK_SIZE = 512


class VoicePipeline:
    def __init__(self):
        print("=" * 70)
        print("🎙️ VOICE — BANGLA TO BANGLISH")
        print("=" * 70)

        print("\n🧠 Initializing components...")

        self.recorder = StreamingRecorder(
            sample_rate=SAMPLE_RATE,
            channels=1,
            device=2,
            chunk_duration=CHUNK_SIZE / SAMPLE_RATE,
        )

        self.vad = SpeechActivityDetector(
            threshold=0.5,
            min_silence_duration_ms=500,
            speech_pad_ms=100,
        )

        self.recognizer = FastBanglaRecognizer()

        self.converter = BanglishConverter()

        self.injector = TextInjector(
            typing_interval=0.005,
        )

        print("✅ Voice pipeline ready.")

    def run(self):
        """
        Start continuous microphone listening.

        Speech is collected between VAD start/end events.
        After speech ends:

            Audio
              ↓
            FastConformer
              ↓
            Bangla
              ↓
            Banglish
              ↓
            Active cursor
        """

        speech_buffer = []

        in_speech = False

        self.recorder.clear_queue()
        self.vad.reset()

        self.recorder.start()

        print("\n" + "=" * 70)
        print("🔴 LISTENING... Speak now")
        print("Press Ctrl+C to stop.")
        print("=" * 70)

        try:
            while True:
                chunk = self.recorder.get_chunk(timeout=1)

                if chunk is None:
                    continue

                chunk = np.asarray(
                    chunk,
                    dtype=np.float32,
                )

                event = self.vad.process(chunk)

                # ------------------------------------------------
                # Speech START
                # ------------------------------------------------

                if event["event"] == "start":

                    in_speech = True
                    speech_buffer = []

                    print("\n🟢 RECORDING...")

                # ------------------------------------------------
                # Collect speech
                # ------------------------------------------------

                if in_speech:
                    speech_buffer.append(chunk)

                # ------------------------------------------------
                # Speech END
                # ------------------------------------------------

                if event["event"] == "end":

                    in_speech = False

                    if not speech_buffer:
                        continue

                    audio = np.concatenate(
                        speech_buffer
                    )

                    duration = (
                        len(audio) / SAMPLE_RATE
                    )

                    print(
                        f"🔴 RECORDING END — "
                        f"{duration:.2f} seconds"
                    )

                    print("🟡 PROCESSING...")

                    # --------------------------------------------
                    # Speech → Bangla
                    # --------------------------------------------

                    bangla_text = self.recognizer.transcribe(
                        audio,
                        SAMPLE_RATE,
                    )

                    if not bangla_text:
                        print("⚠️ No speech recognized.")
                        continue

                    print(
                        f"🇧🇩 Bangla: {bangla_text}"
                    )

                    # --------------------------------------------
                    # Bangla → Banglish
                    # --------------------------------------------

                    banglish_text = self.converter.convert(
                        bangla_text
                    )

                    print(
                        f"🔤 Banglish: {banglish_text}"
                    )

                    # --------------------------------------------
                    # Banglish → Active Cursor
                    # --------------------------------------------

                    if banglish_text:

                        self.injector.type_text(
                            banglish_text + " "
                        )

                        print("⌨️ Typed into active cursor.")

                    print("\n🔴 LISTENING...")

        except KeyboardInterrupt:

            print("\n\n🛑 Stopping Voice...")

        finally:

            self.recorder.stop()

            print("✅ Voice stopped.")


def main():
    pipeline = VoicePipeline()
    pipeline.run()


if __name__ == "__main__":
    main()