import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write


class VoiceRecorder:
    def __init__(self, sample_rate=16000, device=2):
        self.sample_rate = sample_rate
        self.device = device

    def record(self, duration=5):
        print("🎙️ Recording...")

        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            device=self.device,
        )

        sd.wait()

        audio = np.squeeze(audio)

        # Save raw microphone audio for debugging
        write("debug_audio.wav", self.sample_rate, audio)

        print("✅ Recording finished.")
        print(f"Max volume: {np.max(np.abs(audio)):.6f}")
        print(f"Average volume: {np.mean(np.abs(audio)):.6f}")

        return audio