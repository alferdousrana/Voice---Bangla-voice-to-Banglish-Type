import time

import numpy as np

from app.audio.stream_recorder import StreamingRecorder
from app.speech.streaming_recognizer import StreamingBanglaRecognizer


SAMPLE_RATE = 16000
CHUNK_DURATION = 0.5

# Voice detection threshold
VOICE_THRESHOLD = 0.02

# কতক্ষণ silence হলে speech শেষ ধরা হবে
SILENCE_DURATION = 0.8


def main():
    recorder = StreamingRecorder(
        sample_rate=SAMPLE_RATE,
        device=2,
        chunk_duration=CHUNK_DURATION,
    )

    recognizer = StreamingBanglaRecognizer()

    recorder.start()

    print()
    print("🎙️ Speak naturally.")
    print("⏸️ Pause for about 1 second to transcribe.")
    print("🛑 Press Ctrl+C to stop.")
    print()

    speech_buffer = []
    silence_chunks = 0

    required_silence_chunks = int(
        SILENCE_DURATION / CHUNK_DURATION
    )

    try:
        while True:
            chunk = recorder.get_chunk()

            if chunk is None:
                continue

            rms = np.sqrt(np.mean(chunk ** 2))

            # Voice detected
            if rms >= VOICE_THRESHOLD:
                speech_buffer.append(chunk)
                silence_chunks = 0

            # Silence detected
            else:
                if speech_buffer:
                    speech_buffer.append(chunk)
                    silence_chunks += 1

                    if silence_chunks >= required_silence_chunks:
                        audio = np.concatenate(speech_buffer)

                        duration = len(audio) / SAMPLE_RATE

                        print()
                        print(
                            f"🧠 Transcribing "
                            f"({duration:.2f}s)..."
                        )

                        text = recognizer.transcribe(
                            audio,
                            SAMPLE_RATE,
                        )

                        if text:
                            print("📝 Bangla:")
                            print(text)

                        print()

                        speech_buffer = []
                        silence_chunks = 0

    except KeyboardInterrupt:
        print("\n🛑 Stopping...")

    finally:
        recorder.stop()


if __name__ == "__main__":
    main()