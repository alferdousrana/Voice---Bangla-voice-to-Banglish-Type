import numpy as np
import torch
from silero_vad import load_silero_vad, VADIterator


class SpeechActivityDetector:
    """
    Real-time speech activity detector using Silero VAD.

    Input:
        16 kHz mono float32 audio
        512 samples per chunk

    Output:
        speech_start / speech_end events
    """

    SAMPLE_RATE = 16000
    CHUNK_SIZE = 512

    def __init__(
        self,
        threshold=0.5,
        min_silence_duration_ms=500,
        speech_pad_ms=100,
    ):
        print("🧠 Loading Silero VAD...")

        torch.set_num_threads(1)

        self.model = load_silero_vad()

        self.vad = VADIterator(
            self.model,
            threshold=threshold,
            sampling_rate=self.SAMPLE_RATE,
            min_silence_duration_ms=min_silence_duration_ms,
            speech_pad_ms=speech_pad_ms,
        )

        self.in_speech = False

        print("✅ Silero VAD loaded.")

    def process(self, audio_chunk):
        """
        Process one 512-sample audio chunk.

        Returns:
            {
                "event": "start" | "end" | None,
                "timestamp": int | None
            }
        """

        audio_chunk = np.asarray(
            audio_chunk,
            dtype=np.float32,
        )

        if len(audio_chunk) != self.CHUNK_SIZE:
            raise ValueError(
                f"Expected {self.CHUNK_SIZE} samples, "
                f"got {len(audio_chunk)}"
            )

        event = self.vad(audio_chunk)

        if event is None:
            return {
                "event": None,
                "timestamp": None,
            }

        if "start" in event:
            self.in_speech = True

            return {
                "event": "start",
                "timestamp": event["start"],
            }

        if "end" in event:
            self.in_speech = False

            return {
                "event": "end",
                "timestamp": event["end"],
            }

        return {
            "event": None,
            "timestamp": None,
        }

    def reset(self):
        """Reset VAD state."""

        self.vad.reset_states()
        self.in_speech = False