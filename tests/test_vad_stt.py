import time
import numpy as np

from app.audio.stream_recorder import StreamingRecorder
from app.speech.vad import SpeechActivityDetector
from app.speech.streaming_recognizer import StreamingBanglaRecognizer


SAMPLE_RATE = 16000
DEVICE_INDEX = 2
CHUNK_SIZE = 512

MIN_SPEECH_DURATION = 1.0


def show_status(status, message):
    print(f"\r{status} {message:<60}", end="", flush=True)


def main():
    print("🧠 Loading Bengali ASR model...")
    recognizer = StreamingBanglaRecognizer()

    print("🧠 Loading Silero VAD...")
    vad = SpeechActivityDetector(
        threshold=0.5,
        min_silence_duration_ms=500,
        speech_pad_ms=100,
    )

    recorder = StreamingRecorder(
        sample_rate=SAMPLE_RATE,
        device=DEVICE_INDEX,
        chunk_duration=0.032,
    )

    recorder.start()

    print()
    print("=" * 70)
    print("🎙️ LIVE BANGLA SPEECH TEST")
    print("=" * 70)
    print("Speak naturally.")
    print("Pause for about 0.5 second between sentences.")
    print("Press Ctrl+C to stop.")
    print("=" * 70)
    print()

    speech_buffer = []
    speaking = False

    start_time = time.time()

    try:
        while time.time() - start_time < 60:

            chunk = recorder.get_chunk()

            if chunk is None:
                continue

            if len(chunk) != CHUNK_SIZE:
                continue

            result = vad.process(chunk)

            # --------------------------------
            # SPEECH START
            # --------------------------------
            if result["event"] == "start":

                speaking = True
                speech_buffer = []

                speech_buffer.append(chunk)

                print()
                print("🟢 RECORDING... Speech detected")

                continue

            # --------------------------------
            # SPEECH CONTINUING
            # --------------------------------
            if speaking:

                speech_buffer.append(chunk)

                show_status(
                    "🟢",
                    "RECORDING... Keep speaking"
                )

            # --------------------------------
            # SPEECH END
            # --------------------------------
            if result["event"] == "end":

                speaking = False

                if not speech_buffer:
                    continue

                audio = np.concatenate(speech_buffer)

                duration = len(audio) / SAMPLE_RATE

                print()
                print(
                    f"🔴 RECORDING END — "
                    f"{duration:.2f} seconds"
                )

                if duration < MIN_SPEECH_DURATION:

                    print(
                        "⚠️ Speech too short. Ignoring."
                    )

                    speech_buffer = []

                    print()
                    show_status(
                        "🔴",
                        "LISTENING... Speak now"
                    )

                    continue

                print("🟡 PROCESSING... Transcribing...")

                transcribe_start = time.time()

                try:

                    text = recognizer.transcribe(
                        audio,
                        SAMPLE_RATE,
                    )

                    transcribe_time = time.time() - transcribe_start

                    print(
                        f"⏱️ Transcription time: "
                        f"{transcribe_time:.2f}s"
                    )

                    if text:

                        print()
                        print("🇧🇩 Bangla:")
                        print(text)
                        print()

                    else:

                        print(
                            "⚠️ No speech recognized."
                        )

                except Exception as e:

                    print()
                    print(f"❌ STT error: {e}")

                speech_buffer = []

                print()
                show_status(
                    "🔴",
                    "LISTENING... Speak now"
                )

    except KeyboardInterrupt:

        print()
        print()
        print("🛑 Stopping...")

    finally:

        recorder.stop()
        vad.reset()

        print()
        print("✅ Test finished.")


if __name__ == "__main__":
    main()