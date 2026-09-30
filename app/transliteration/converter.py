import re

from app.speech.corrector import BanglaCorrectionEngine
from app.transliteration.dictionary import (
    CUSTOM_PHRASES,
    CUSTOM_WORDS,
    WORD_MAP,
)
from app.transliteration.dictionary_manager import DictionaryManager
from app.transliteration.unknown_words import save_unknown_words
from app.utils.text_normalize import normalize_bangla, normalize_dict_keys


BANGLA = r"\u0980-\u09FF"

TOKEN_PATTERN = re.compile(
    rf"[{BANGLA}]+|[A-Za-z0-9_]+|\s+|[^\w\s]",
    re.UNICODE,
)

BANGLA_WORD = re.compile(rf"[{BANGLA}]+")

# ASR fragments like "খ", "জ", "ম" are not real words.
MIN_UNKNOWN_LENGTH = 2


class BanglishConverter:
    def __init__(self, dictionary_manager=None):
        self.dictionary_manager = dictionary_manager or DictionaryManager()
        self.corrector = BanglaCorrectionEngine()

        # Normalize built-in dictionaries once.
        self.word_map = normalize_dict_keys(WORD_MAP)
        self.custom_words = normalize_dict_keys(CUSTOM_WORDS)
        self.custom_phrases = normalize_dict_keys(CUSTOM_PHRASES)

    # -------------------------------------------------

    def normalize_bangla(self, text):
        return normalize_bangla(text)

    def lookup_word(self, word):
        word = normalize_bangla(word)

        return (
            self.dictionary_manager.get_word(word)
            or self.custom_words.get(word)
            or self.word_map.get(word)
        )

    def get_dictionary_words(self):
        words = set(self.word_map)
        words.update(self.custom_words)
        words.update(self.dictionary_manager.get_all_words())
        return words

    def apply_custom_phrases(self, text):
        phrases = dict(self.custom_phrases)
        phrases.update(self.dictionary_manager.get_all_phrases())

        for bangla, banglish in sorted(
            phrases.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        ):
            # Whole-word match only (no replacing inside another word).
            pattern = rf"(?<![{BANGLA}]){re.escape(bangla)}(?![{BANGLA}])"
            text = re.sub(pattern, banglish, text)

        return text

    def tokenize(self, text):
        return TOKEN_PATTERN.findall(text)

    # -------------------------------------------------

    def convert_with_unknowns(self, text):
        text = normalize_bangla(text)

        if not text:
            return "", []

        text = self.corrector.correct(
            text,
            dictionary_words=self.get_dictionary_words(),
        )

        text = self.apply_custom_phrases(text)

        output = []
        unknown_words = []

        for token in self.tokenize(text):
            if not token:
                continue

            if BANGLA_WORD.fullmatch(token):
                banglish = self.lookup_word(token)

                if banglish:
                    output.append(banglish)
                else:
                    output.append(f"[UNKNOWN:{token}]")
                    unknown_words.append(token)
            else:
                output.append(token)

        result = "".join(output)
        result = re.sub(r"\s+([,.!?;:])", r"\1", result)

        to_save = [w for w in unknown_words if len(w) >= MIN_UNKNOWN_LENGTH]

        if to_save:
            save_unknown_words(to_save)

        return result, unknown_words

    def convert(self, text):
        result, _ = self.convert_with_unknowns(text)
        return result