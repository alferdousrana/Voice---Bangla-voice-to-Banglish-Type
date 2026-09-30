import json
from difflib import SequenceMatcher
from pathlib import Path

from app.utils.text_normalize import normalize_bangla


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
CORRECTIONS_FILE = DATA_DIR / "corrections.json"

FUZZY_THRESHOLD = 0.84
FUZZY_MIN_LENGTH = 4          # short words are too risky to "fix"


PHONETIC_CORRECTIONS = {
    "গেসে": "গেছে",
    "গিয়ে আছে": "গেছে",
    "চার্স": "চার্জ",
    "পম্পিউটার": "কম্পিউটার",
    "ভয়েশ": "ভয়েস",
    "ভয়েজ": "ভয়েস",
    "জ পি": "জিপি",
    "হ্যালো হ": "হ্যালো",
    "হেলো": "হ্যালো",
}


class BanglaCorrectionEngine:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        self.corrections = {}
        self._load()

        self.phonetic_corrections = {
            normalize_bangla(k): normalize_bangla(v)
            for k, v in PHONETIC_CORRECTIONS.items()
        }

        self._fuzzy_cache = {}
        self._candidates_key = None
        self._by_length = {}

    # -------------------------------------------------
    # STORAGE
    # -------------------------------------------------

    def _load(self):
        if not CORRECTIONS_FILE.exists() or CORRECTIONS_FILE.stat().st_size == 0:
            self._save()
            return

        try:
            with open(CORRECTIONS_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, dict):
                self.corrections = {
                    normalize_bangla(k): normalize_bangla(v)
                    for k, v in data.items()
                }
        except (json.JSONDecodeError, OSError):
            self.corrections = {}

    def _save(self):
        with open(CORRECTIONS_FILE, "w", encoding="utf-8") as file:
            json.dump(self.corrections, file, ensure_ascii=False, indent=4)

    def add_correction(self, wrong, correct):
        wrong, correct = normalize_bangla(wrong), normalize_bangla(correct)

        if wrong and correct:
            self.corrections[wrong] = correct
            self._save()

    def remove_correction(self, wrong):
        wrong = normalize_bangla(wrong)

        if self.corrections.pop(wrong, None) is not None:
            self._save()

    def get_corrections(self):
        return dict(self.corrections)

    def correct_and_learn(self, wrong, correct):
        self.add_correction(wrong, correct)
        return correct

    # -------------------------------------------------
    # CORRECTION
    # -------------------------------------------------

    def _normalize(self, text):
        return normalize_bangla(text)

    def _correct_phrase(self, text):
        rules = dict(self.phonetic_corrections)
        rules.update(self.corrections)

        tokens = text.split(" ")
        # Replace whole words / whole word sequences only.
        padded = f" {' '.join(tokens)} "

        for wrong, correct in sorted(
            rules.items(), key=lambda item: len(item[0]), reverse=True
        ):
            padded = padded.replace(f" {wrong} ", f" {correct} ")

        return padded.strip()

    def _index_candidates(self, candidates):
        key = hash(frozenset(candidates))

        if key == self._candidates_key:
            return

        self._by_length = {}

        for word in candidates:
            if len(word) >= FUZZY_MIN_LENGTH - 1:
                self._by_length.setdefault(len(word), []).append(word)

        self._candidates_key = key
        self._fuzzy_cache.clear()

    def _fuzzy_correct_word(self, word):
        if len(word) < FUZZY_MIN_LENGTH:
            return word

        if word in self._fuzzy_cache:
            return self._fuzzy_cache[word]

        best, best_score = word, 0.0

        # Only compare with words of similar length (fast + safer).
        for length in (len(word) - 1, len(word), len(word) + 1):
            for candidate in self._by_length.get(length, ()):
                score = SequenceMatcher(None, word, candidate).ratio()

                if score > best_score:
                    best, best_score = candidate, score

        result = best if best_score >= FUZZY_THRESHOLD else word
        self._fuzzy_cache[word] = result

        return result

    def correct(self, text, dictionary_words=None):
        if not text:
            return ""

        text = self._correct_phrase(normalize_bangla(text))

        if not dictionary_words:
            return text

        known = (
            dictionary_words
            if isinstance(dictionary_words, set)
            else set(dictionary_words)
        )

        self._index_candidates(known)

        return " ".join(
            token if token in known else self._fuzzy_correct_word(token)
            for token in text.split()
        )