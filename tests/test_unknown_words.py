from app.transliteration.unknown_words import (
    load_unknown_words,
    save_unknown_words,
)


def test_unknown_words_are_saved(tmp_path, monkeypatch):

    import app.transliteration.unknown_words as module

    test_file = tmp_path / "unknown_words.json"

    monkeypatch.setattr(
        module,
        "UNKNOWN_WORDS_FILE",
        test_file,
    )

    save_unknown_words(
        ["খুব", "সুন্দর"]
    )

    assert load_unknown_words() == [
        "খুব",
        "সুন্দর",
    ]


def test_duplicate_words_are_not_saved(tmp_path, monkeypatch):

    import app.transliteration.unknown_words as module

    test_file = tmp_path / "unknown_words.json"

    monkeypatch.setattr(
        module,
        "UNKNOWN_WORDS_FILE",
        test_file,
    )

    save_unknown_words(
        ["খুব", "সুন্দর"]
    )

    save_unknown_words(
        ["খুব", "সুন্দর", "নতুন"]
    )

    assert load_unknown_words() == [
        "খুব",
        "নতুন",
        "সুন্দর",
]


def test_empty_words_are_ignored(tmp_path, monkeypatch):

    import app.transliteration.unknown_words as module

    test_file = tmp_path / "unknown_words.json"

    monkeypatch.setattr(
        module,
        "UNKNOWN_WORDS_FILE",
        test_file,
    )

    save_unknown_words(
        ["", "   "]
    )

    assert load_unknown_words() == []