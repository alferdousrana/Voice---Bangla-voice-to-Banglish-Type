import numpy as np
import torch
from transformers import pipeline


MODEL_NAME = "bangla-speech-processing/BanglaASR"


class StreamingBanglaRecognizer:
    def __init__(self):
        print("🧠 Loading Bengali ASR model...")
        print(f"📦 Model: {MODEL_NAME}")

        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        self.device = device

        print(f"💻 Device: {device}")

        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=MODEL_NAME,
            device=device,
            dtype=dtype,
        )

        print("✅ Bengali ASR model loaded.")

    def transcribe(self, audio, sample_rate=16000):
        if audio is None or len(audio) == 0:
            return ""

        audio = np.asarray(audio, dtype=np.float32)

        # Safety normalization only if necessary
        peak = np.max(np.abs(audio))

        if peak > 1.0:
            audio = audio / peak

        result = self.pipe(
            {
                "raw": audio,
                "sampling_rate": sample_rate,
            },
            generate_kwargs={
                "language": "bengali",
                "task": "transcribe",
            },
        )

        return result["text"].strip()