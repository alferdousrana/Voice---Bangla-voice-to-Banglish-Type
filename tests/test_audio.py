from app.audio.recorder import VoiceRecorder


def main():
    recorder = VoiceRecorder()

    audio = recorder.record(duration=5)

    print(f"Audio samples: {len(audio)}")
    print(f"Audio duration: {len(audio) / recorder.sample_rate:.2f} seconds")


if __name__ == "__main__":
    main()