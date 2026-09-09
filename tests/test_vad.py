
import time
import numpy as np

from app.audio.stream_recorder import StreamingRecorder
from app.speech.vad import SpeechActivityDetector


SAMPLE_RATE = 16000
DEVICE_INDEX = 2


def main():
    recorder = StreamingRecorder(
        sample_rate=SAMPLE_RATE,
        device=DEVICE_INDEX,
        chunk_duration=0.032,
    )

    vad = SpeechActivityDetector(
        threshold=0.5,
        min_silence_duration_ms=500,
        speech_pad_ms=100,
    )

    recorder.start()

    print()
    print("🎙️ VAD test started.")
    print("Speak naturally.")
    print("Pause between sentences.")
    print("Press Ctrl+C to stop.")
    print()

    start_time = time.time()

    try:
        while time.time() - start_time < 30:

            chunk = recorder.get_chunk()

            if chunk is None:
                continue

            if len(chunk) != 512:
                continue

            result = vad.process(chunk)

            if result["event"] == "start":
                print("🟢 SPEECH START")

            elif result["event"] == "end":
                print("🔴 SPEECH END")

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")

    finally:
        recorder.stop()

    print("✅ VAD test finished.")


if __name__ == "__main__":
    main()