import json
from pathlib import Path

from app.utils.text_normalize import normalize_bangla, normalize_dict_keys


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"

WORDS_FILE = DATA_DIR / "personal_words.json"
PHRASES_FILE = DATA_DIR / "personal_phrases.json"


class DictionaryManager:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        self.words = {}
        self.phrases = {}

        self._words_mtime = None
        self._phrases_mtime = None

        self._refresh_words()
        self._refresh_phrases()

    @staticmethod
    def _load(file_path: Path):
        if not file_path.exists():
            return {}

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            return normalize_dict_keys(data) if isinstance(data, dict) else {}

        except (json.JSONDecodeError, OSError):
            return {}

    @staticmethod
    def _save(file_path: Path, data: dict):
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4,
            )

    @staticmethod
    def _mtime(file_path: Path):
        try:
            return file_path.stat().st_mtime_ns
        except OSError:
            return None

    def _refresh_words(self):
        current_mtime = self._mtime(WORDS_FILE)

        if current_mtime != self._words_mtime:
            self.words = self._load(WORDS_FILE)
            self._words_mtime = current_mtime

    def _refresh_phrases(self):
        current_mtime = self._mtime(PHRASES_FILE)

        if current_mtime != self._phrases_mtime:
            self.phrases = self._load(PHRASES_FILE)
            self._phrases_mtime = current_mtime

    # -------------------------
    # WORDS
    # -------------------------

    def add_word(self, bangla: str, banglish: str):
        bangla = normalize_bangla(bangla)
        banglish = banglish.strip()

        if not bangla or not banglish:
            return False

        self._refresh_words()

        self.words[bangla] = banglish
        self._save(WORDS_FILE, self.words)

        self._words_mtime = self._mtime(WORDS_FILE)

        return True

    def remove_word(self, bangla: str):
        bangla = normalize_bangla(bangla)
        self._refresh_words()

        if bangla not in self.words:
            return False

        del self.words[bangla]
        self._save(WORDS_FILE, self.words)

        self._words_mtime = self._mtime(WORDS_FILE)

        return True

    def get_word(self, bangla: str):
        self._refresh_words()
        return self.words.get(normalize_bangla(bangla))

    def get_all_words(self):
        self._refresh_words()
        return dict(self.words)

    # -------------------------
    # PHRASES
    # -------------------------

    def add_phrase(self, bangla: str, banglish: str):
        bangla = normalize_bangla(bangla)
        banglish = banglish.strip()

        if not bangla or not banglish:
            return False

        self._refresh_phrases()

        self.phrases[bangla] = banglish
        self._save(PHRASES_FILE, self.phrases)

        self._phrases_mtime = self._mtime(PHRASES_FILE)

        return True

    def remove_phrase(self, bangla: str):
        bangla = normalize_bangla(bangla)
        self._refresh_phrases()

        if bangla not in self.phrases:
            return False

        del self.phrases[bangla]
        self._save(PHRASES_FILE, self.phrases)

        self._phrases_mtime = self._mtime(PHRASES_FILE)

        return True

    def get_phrase(self, bangla: str):
        self._refresh_phrases()
        return self.phrases.get(normalize_bangla(bangla))

    def get_all_phrases(self):
        self._refresh_phrases()
        return dict(self.phrases)