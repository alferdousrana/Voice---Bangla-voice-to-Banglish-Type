import numpy as np

from app.audio.recorder import VoiceRecorder
from app.speech.recognizer import SpeechRecognizer


def main():
    recorder = VoiceRecorder()

    audio = recorder.record(duration=5)

    print("\n🔍 Audio information:")
    print(f"Samples: {len(audio)}")
    print(f"Max volume: {np.max(np.abs(audio)):.6f}")
    print(f"Average volume: {np.mean(np.abs(audio)):.6f}")

    recognizer = SpeechRecognizer()

    text = recognizer.transcribe(audio)

    print("\n📝 Recognized text:")
    print(text)


if __name__ == "__main__":
    main()