import sounddevice as sd
import numpy as np


DEVICE_INDEX = 2
SAMPLE_RATE = 16000
DURATION = 5


print(f"Using device: {DEVICE_INDEX}")
print("🎙️ Speak now...")

audio = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="float32",
    device=DEVICE_INDEX,
)

sd.wait()

audio = np.squeeze(audio)

print("\n🔍 Result:")
print(f"Max volume: {np.max(np.abs(audio)):.6f}")
print(f"Average volume: {np.mean(np.abs(audio)):.6f}")