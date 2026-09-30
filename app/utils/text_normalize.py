# app/utils/text_normalize.py
"""
Single source of truth for Bangla text normalization.

Why: "য়", "ড়", "ঢ়" can be written two ways in Unicode
(precomposed U+09DF or য + nukta U+09AF U+09BC). ASR output,
dictionary.py and personal_words.json were using different
forms, so many known words never matched.

Every place that stores or looks up Bangla text must call
normalize_bangla().
"""

import re
import unicodedata


# Zero-width chars + the replacement char "�" that appears when
# Whisper output is cut in the middle of a UTF-8 byte sequence.
_INVISIBLE = re.compile(r"[\u200b\u200c\u200d\u2060\ufeff\ufffd]")
_SPACES = re.compile(r"\s+")


def normalize_bangla(text) -> str:
    if not text:
        return ""

    text = unicodedata.normalize("NFC", str(text))
    text = _INVISIBLE.sub("", text)
    text = _SPACES.sub(" ", text)

    return text.strip()


def normalize_dict_keys(data: dict) -> dict:
    result = {}

    for key, value in data.items():
        if not isinstance(key, str) or not isinstance(value, str):
            continue

        key = normalize_bangla(key)
        value = value.strip()

        if key and value:
            result[key] = value

    return result