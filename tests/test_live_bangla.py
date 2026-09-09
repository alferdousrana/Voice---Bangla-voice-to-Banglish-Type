import torch
import sounddevice as sd
import numpy as np
from transformers import pipeline


MODEL_NAME = "asif00/whisper-bangla"

SAMPLE_RATE = 16000
DURATION = 5
DEVICE_INDEX = 2


def main():
    print("Loading Bengali Whisper model...")

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    pipe = pipeline(
        "automatic-speech-recognition",
        model=MODEL_NAME,
        device=device,
        dtype=dtype,
    )

    print("Model loaded.")
    print()

    print("🎙️ Speak now...")
    print("Recording for 5 seconds...")

    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        device=DEVICE_INDEX,
    )

    sd.wait()

    audio = np.squeeze(audio)

    print("✅ Recording finished.")
    print()
    print("🧠 Transcribing...")

    result = pipe(
        audio,
        generate_kwargs={
            "language": "bengali",
            "task": "transcribe",
        },
    )

    text = result["text"].strip()

    print()
    print("📝 Recognized Bangla:")
    print(text)


if __name__ == "__main__":
    main()