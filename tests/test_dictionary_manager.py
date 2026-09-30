from app.transliteration.dictionary_manager import (
    DictionaryManager,
)


def test_add_word(tmp_path, monkeypatch):

    import app.transliteration.dictionary_manager as module

    words_file = tmp_path / "personal_words.json"
    phrases_file = tmp_path / "personal_phrases.json"

    monkeypatch.setattr(
        module,
        "WORDS_FILE",
        words_file,
    )

    monkeypatch.setattr(
        module,
        "PHRASES_FILE",
        phrases_file,
    )

    manager = DictionaryManager()

    assert manager.add_word(
        "মাহিম",
        "mahim",
    )

    assert manager.get_word(
        "মাহিম"
    ) == "mahim"


def test_bangla_is_saved_as_utf8(
    tmp_path,
    monkeypatch,
):

    import app.transliteration.dictionary_manager as module

    words_file = tmp_path / "personal_words.json"
    phrases_file = tmp_path / "personal_phrases.json"

    monkeypatch.setattr(
        module,
        "WORDS_FILE",
        words_file,
    )

    monkeypatch.setattr(
        module,
        "PHRASES_FILE",
        phrases_file,
    )

    manager = DictionaryManager()

    manager.add_word(
        "মাহিম",
        "mahim",
    )

    with open(
        words_file,
        "r",
        encoding="utf-8",
    ) as file:

        content = file.read()

    assert "মাহিম" in content
    assert "mahim" in content


def test_remove_word(
    tmp_path,
    monkeypatch,
):

    import app.transliteration.dictionary_manager as module

    words_file = tmp_path / "personal_words.json"
    phrases_file = tmp_path / "personal_phrases.json"

    monkeypatch.setattr(
        module,
        "WORDS_FILE",
        words_file,
    )

    monkeypatch.setattr(
        module,
        "PHRASES_FILE",
        phrases_file,
    )

    manager = DictionaryManager()

    manager.add_word(
        "মাহিম",
        "mahim",
    )

    assert manager.remove_word(
        "মাহিম"
    )

    assert manager.get_word(
        "মাহিম"
    ) is None