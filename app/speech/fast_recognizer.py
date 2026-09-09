import time

import numpy as np
import nemo.collections.asr as nemo_asr


MODEL_NAME = "hishab/titu_stt_bn_fastconformer"


class FastBanglaRecognizer:
    def __init__(self):
        print("🧠 Loading Fast Bengali ASR model...")
        print(f"📦 Model: {MODEL_NAME}")

        start_time = time.time()

        self.model = nemo_asr.models.ASRModel.from_pretrained(
            model_name=MODEL_NAME
        )

        elapsed = time.time() - start_time

        self.model.eval()

        print(f"⏱️ Model loading time: {elapsed:.2f}s")
        print("✅ Fast Bengali ASR model loaded.")

    def transcribe(self, audio, sample_rate=16000):
        if audio is None or len(audio) == 0:
            return ""

        audio = np.asarray(audio, dtype=np.float32)

        peak = np.max(np.abs(audio))

        if peak > 1.0:
            audio = audio / peak

        duration = len(audio) / sample_rate

        print(f"🎙️ Audio duration: {duration:.2f}s")

        start_time = time.time()

        # NeMo expects an audio file path for this model.
        # Save temporary audio for transcription.
        import tempfile
        import wave

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False,
        ) as temp_file:
            temp_path = temp_file.name

        audio_int16 = np.clip(audio, -1.0, 1.0)
        audio_int16 = (audio_int16 * 32767).astype(np.int16)

        with wave.open(temp_path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_int16.tobytes())

        try:
            output = self.model.transcribe(
                [temp_path],
                batch_size=1,
            )

            if isinstance(output, tuple):
                output = output[0]

            if not output:
                return ""

            result = output[0]

            if hasattr(result, "text"):
                text = result.text
            else:
                text = str(result)

            text = text.strip()

        finally:
            import os

            try:
                os.remove(temp_path)
            except OSError:
                pass

        elapsed = time.time() - start_time

        print(f"⏱️ Transcription time: {elapsed:.2f}s")

        if duration > 0:
            realtime_factor = elapsed / duration
            print(f"⚡ Real-time factor: {realtime_factor:.2f}x")

        return text