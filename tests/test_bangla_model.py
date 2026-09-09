import torch
from transformers import pipeline
from scipy.io import wavfile


MODEL_NAME = "asif00/whisper-bangla"


def main():
    print("Loading Bengali Whisper model...")

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    print(f"Device: {device}")

    pipe = pipeline(
        "automatic-speech-recognition",
        model=MODEL_NAME,
        device=device,
        torch_dtype=dtype,
    )

    print("Model loaded.")

    sample_rate, audio = wavfile.read("debug_audio.wav")

    print(f"Sample rate: {sample_rate}")
    print(f"Audio samples: {len(audio)}")

    print("\nTranscribing...")

    result = pipe(
        audio,
        generate_kwargs={
            "language": "bengali",
            "task": "transcribe",
        },
    )

    print("\n📝 Recognized text:")
    print(result["text"])


if __name__ == "__main__":
    main()