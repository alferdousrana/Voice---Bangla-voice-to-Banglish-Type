from faster_whisper import WhisperModel


class SpeechRecognizer:
    def __init__(self, model_size="medium"):
        print("Loading speech recognition model...")

        self.model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8",
        )

        print("Speech recognition model loaded.")

    def transcribe(self, audio):
        segments, info = self.model.transcribe(
            audio,
            language="bn",
            task="transcribe",
            beam_size=5,
            initial_prompt="বাংলা ভাষায় পরিষ্কারভাবে লিখুন।",
            condition_on_previous_text=False,
        )

        text = " ".join(
            segment.text.strip()
            for segment in segments
        )

        return text.strip()