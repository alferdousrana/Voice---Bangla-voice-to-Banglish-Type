# app/transliteration/unknown_words.py

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

UNKNOWN_WORDS_FILE = (
    PROJECT_ROOT / "unknown_words.json"
)


def load_unknown_words():

    if not UNKNOWN_WORDS_FILE.exists():
        return []

    try:

        with open(
            UNKNOWN_WORDS_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        if isinstance(data, list):
            return data

    except (
        json.JSONDecodeError,
        OSError,
    ):
        pass

    return []


def save_unknown_words(words):

    if not words:
        return

    existing = load_unknown_words()

    for word in words:

        word = word.strip()

        if (
            word
            and word not in existing
        ):
            existing.append(word)

    existing.sort()

    with open(
        UNKNOWN_WORDS_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            existing,
            file,
            ensure_ascii=False,
            indent=4,
        )


def remove_unknown_word(word):

    word = word.strip()

    if not word:
        return False

    existing = load_unknown_words()

    if word not in existing:
        return False

    existing.remove(word)

    with open(
        UNKNOWN_WORDS_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            existing,
            file,
            ensure_ascii=False,
            indent=4,
        )

    return True


def collect_unknown_words(words):

    save_unknown_words(words)

    return load_unknown_words()