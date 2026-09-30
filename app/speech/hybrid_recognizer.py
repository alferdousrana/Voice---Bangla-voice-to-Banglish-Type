import logging
import threading
import time
import zlib

import numpy as np
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

from app.speech.fast_recognizer import FastBanglaRecognizer
from app.utils.text_normalize import normalize_bangla


logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)


WHISPER_MODEL = "bangla-speech-processing/BanglaASR"

# Bangla text costs roughly 1-3 Whisper tokens PER CHARACTER.
# The old value (32) cut sentences after ~10-15 letters, which is
# why "খাই" became "খা" and "�" appeared at the end.
MAX_NEW_TOKENS = 220

# Beam search is noticeably more accurate than greedy decoding.
BEAMS_GPU = 4
BEAMS_CPU = 2

MIN_AUDIO_SECONDS = 0.35
MAX_AUDIO_SECONDS = 29.0          # Whisper window is 30 s

TARGET_RMS = 0.08                 # gentle loudness normalization
MAX_GAIN = 8.0

# Whisper's own hallucination check: repetitive garbage like
# "যোগ্যোগ্যোগ্যোগ্..." compresses very well.
MAX_COMPRESSION_RATIO = 2.4


class HybridBanglaRecognizer:
    def __init__(self):
        self.sample_rate = 16000
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.num_beams = BEAMS_GPU if self.device == "cuda" else BEAMS_CPU

        self.fallback = None
        self._lock = threading.Lock()

        print(f"🧠 Loading Bengali ASR on {self.device.upper()}...")

        start = time.perf_counter()

        self.processor = AutoProcessor.from_pretrained(WHISPER_MODEL)

        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            WHISPER_MODEL,
            dtype=self.dtype,
        )

        self.model.to(self.device)
        self.model.eval()

        self.model.generation_config.language = "bengali"
        self.model.generation_config.task = "transcribe"
        self.model.generation_config.forced_decoder_ids = None

        self._warmup()

        print(
            f"✅ ASR ready ({time.perf_counter() - start:.1f}s) "
            f"| beams={self.num_beams}"
        )

        if self.device == "cpu":
            print(
                "⚠️ Running on CPU. A CUDA build of PyTorch "
                "will be much faster."
            )

    # -------------------------------------------------
    # AUDIO
    # -------------------------------------------------

    def _prepare_audio(self, audio):
        audio = np.asarray(audio, dtype=np.float32).reshape(-1)

        if audio.size == 0:
            return None

        audio = np.nan_to_num(audio)
        audio = audio - float(np.mean(audio))          # remove DC offset

        duration = audio.size / self.sample_rate

        if duration < MIN_AUDIO_SECONDS:
            return None

        if duration > MAX_AUDIO_SECONDS:
            audio = audio[: int(MAX_AUDIO_SECONDS * self.sample_rate)]

        # RMS normalization with a gain limit.
        # (Peak normalization boosted background noise on quiet
        # clips and made Whisper hallucinate.)
        rms = float(np.sqrt(np.mean(audio ** 2)))

        if rms > 1e-5:
            gain = min(TARGET_RMS / rms, MAX_GAIN)
            audio = audio * gain

        return np.clip(audio, -1.0, 1.0)

    # -------------------------------------------------
    # WHISPER
    # -------------------------------------------------

    def _warmup(self):
        try:
            silence = np.zeros(self.sample_rate, dtype=np.float32)
            self._transcribe_whisper(silence, max_new_tokens=4)
        except Exception:
            pass

    def _transcribe_whisper(self, audio, max_new_tokens=MAX_NEW_TOKENS):
        inputs = self.processor(
            audio,
            sampling_rate=self.sample_rate,
            return_tensors="pt",
        )

        input_features = inputs.input_features.to(
            self.device,
            dtype=self.dtype,
        )

        with self._lock, torch.inference_mode():
            predicted_ids = self.model.generate(
                input_features,
                language="bengali",
                task="transcribe",
                max_new_tokens=max_new_tokens,
                num_beams=self.num_beams,
                do_sample=False,
            )

        text = self.processor.batch_decode(
            predicted_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )[0]

        return normalize_bangla(text)

    @staticmethod
    def _looks_like_hallucination(text):
        if len(text) < 12:
            return False

        data = text.encode("utf-8")
        ratio = len(data) / len(zlib.compress(data))

        return ratio > MAX_COMPRESSION_RATIO

    def _get_fallback(self):
        if self.fallback is None:
            self.fallback = FastBanglaRecognizer()

        return self.fallback

    # -------------------------------------------------
    # PUBLIC
    # -------------------------------------------------

    def transcribe(self, audio, sample_rate=16000):
        if sample_rate != self.sample_rate:
            raise ValueError(
                f"Expected {self.sample_rate} Hz audio, got {sample_rate} Hz"
            )

        audio = self._prepare_audio(audio)

        if audio is None:
            return ""

        try:
            text = self._transcribe_whisper(audio)

            if text and not self._looks_like_hallucination(text):
                return text

            if text:
                print(f"⚠️ Whisper hallucination discarded: {text[:40]}...")

        except Exception as exc:
            print(f"⚠️ Whisper failed: {exc}")

        try:
            return normalize_bangla(
                self._get_fallback().transcribe(audio, sample_rate)
            )
        except Exception as exc:
            print(f"❌ ASR failed: {exc}")
            return ""


# =====================================================
# SHARED INSTANCE (load the model only once per app run)
# =====================================================

_recognizer = None
_recognizer_lock = threading.Lock()


def get_recognizer():
    global _recognizer

    with _recognizer_lock:
        if _recognizer is None:
            _recognizer = HybridBanglaRecognizer()

        return _recognizer