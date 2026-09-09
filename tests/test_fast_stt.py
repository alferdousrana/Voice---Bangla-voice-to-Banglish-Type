from scipy.io import wavfile

from app.speech.fast_recognizer import FastBanglaRecognizer


AUDIO_FILE = "debug_audio.wav"


def main():
    print("=" * 70)
    print("🚀 FAST BENGALI ASR BENCHMARK")
    print("=" * 70)

    print("\n🧠 Loading model...")
    recognizer = FastBanglaRecognizer()

    print("\n🎵 Loading audio...")
    sample_rate, audio = wavfile.read(AUDIO_FILE)

    print(f"Sample rate: {sample_rate}")
    print(f"Samples: {len(audio)}")
    print(f"Duration: {len(audio) / sample_rate:.2f}s")

    print("\n📝 Transcribing...")
    text = recognizer.transcribe(audio, sample_rate)

    print("\n" + "=" * 70)
    print("🇧🇩 RESULT")
    print("=" * 70)
    print(text)
    print("=" * 70)


if __name__ == "__main__":
    main()