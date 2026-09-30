import numpy as np
import torch
from silero_vad import load_silero_vad, VADIterator


class SpeechActivityDetector:
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 512

    def __init__(
        self,
        threshold=0.5,
        min_silence_duration_ms=900,
        speech_pad_ms=150,
        min_volume=0.015,
        noise_multiplier=2.0,
    ):
        torch.set_num_threads(1)

        print("🧠 Loading Silero VAD...")
        self.model = load_silero_vad()
        print("✅ Silero VAD loaded.")

        self.threshold = threshold
        self.min_silence_duration_ms = min_silence_duration_ms
        self.speech_pad_ms = speech_pad_ms
        self.min_volume = min_volume
        self.noise_multiplier = noise_multiplier

        self.vad = VADIterator(
            self.model,
            threshold=self.threshold,
            sampling_rate=self.SAMPLE_RATE,
            min_silence_duration_ms=self.min_silence_duration_ms,
            speech_pad_ms=self.speech_pad_ms,
        )

        self.in_speech = False
        self.noise_floor = 0.005
        self.last_volume = 0.0

        print(f"🎚️ VAD threshold: {self.threshold}")
        print(f"⏱️ Minimum silence: {self.min_silence_duration_ms} ms")
        print(f"🎧 Speech padding: {self.speech_pad_ms} ms")
        print(f"🔊 Minimum volume: {self.min_volume}")

    def _calculate_volume(self, audio):
        audio = np.asarray(audio, dtype=np.float32)

        if audio.size == 0:
            return 0.0

        rms = float(np.sqrt(np.mean(np.square(audio))))
        peak = float(np.max(np.abs(audio)))

        return max(rms, peak * 0.35)

    def _is_loud_enough(self, volume):
        dynamic_threshold = max(
            self.min_volume,
            self.noise_floor * self.noise_multiplier,
        )

        return volume >= dynamic_threshold

    def _update_noise_floor(self, volume):
        if self.in_speech:
            return

        self.noise_floor = (
            self.noise_floor * 0.95
            + volume * 0.05
        )

    def process(self, audio_chunk):
        audio_chunk = np.asarray(audio_chunk, dtype=np.float32)

        if audio_chunk.ndim != 1:
            audio_chunk = audio_chunk.reshape(-1)

        if audio_chunk.size != self.CHUNK_SIZE:
            raise ValueError(
                f"Expected {self.CHUNK_SIZE} samples, "
                f"got {audio_chunk.size}"
            )

        if not np.isfinite(audio_chunk).all():
            audio_chunk = np.nan_to_num(audio_chunk)

        volume = self._calculate_volume(audio_chunk)
        self.last_volume = volume

        self._update_noise_floor(volume)

        loud_enough = self._is_loud_enough(volume)

        event = None

        if loud_enough:
            event = self.vad(audio_chunk)
        else:
            if self.in_speech:
                event = self.vad(audio_chunk)

        if event is not None:
            if "start" in event:
                self.in_speech = True
                return "start"

            if "end" in event:
                self.in_speech = False
                return "end"

        return None

    def get_volume(self):
        return self.last_volume

    def get_noise_floor(self):
        return self.noise_floor

    def get_threshold(self):
        return max(
            self.min_volume,
            self.noise_floor * self.noise_multiplier,
        )

    def reset(self):
        try:
            self.vad.reset_states()
        except Exception:
            pass

        self.in_speech = False
        self.last_volume = 0.0
        self.noise_floor = 0.005