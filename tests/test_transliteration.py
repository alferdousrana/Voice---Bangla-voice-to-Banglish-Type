from app.transliteration.converter import BanglishConverter


converter = BanglishConverter()


def test_basic_sentence():
    text = "আমি আজকে অফিসে যাব না"

    assert converter.convert(text) == (
        "ami ajke office e jabo na"
    )


def test_project_sentence():
    text = "ভাই কালকে প্রজেক্টটা শেষ করে দিও"

    assert converter.convert(text) == (
        "bhai kalke project ta sesh kore dio"
    )


def test_mobile_sentence():
    text = "আমার মোবাইলটা ভেঙে গেছে"

    assert converter.convert(text) == (
        "amar mobile ta venge geche"
    )


def test_location_sentence():
    text = "তুমি এখন কোথায় আছো"

    assert converter.convert(text) == (
        "tumi ekhon kothay acho"
    )


def test_phone_sentence():
    text = "বাসায় গিয়ে আমাকে ফোন দিও"

    assert converter.convert(text) == (
        "basay giye amake phone dio"
    )


def test_work_sentence():
    text = "আমি এখন কম্পিউটারে কাজ করছি"

    assert converter.convert(text) == (
        "ami ekhon computer e kaj korchi"
    )


def test_custom_word():
    text = "আমি কাজ করতেছি"

    assert converter.convert(text) == (
        "ami kaj kortesi"
    )


def test_custom_phrase():
    text = "কাজটা শেষ করে দিও"

    assert converter.convert(text) == (
        "kajta sesh kore dio"
    )


def test_long_custom_phrase_priority():
    text = "শেষ করে দিও"

    assert converter.convert(text) == (
        "sesh kore dio"
    )


def test_mixed_english():
    text = "আমি Django project এ কাজ করছি"

    assert converter.convert(text) == (
        "ami Django project e kaj korchi"
    )


def test_punctuation():
    text = "আমি আজকে অফিসে যাব না।"

    assert converter.convert(text) == (
        "ami ajke office e jabo na।"
    )


def test_unknown_word():
    text = "আমি আজকে খুব অফিসে যাব"

    result = converter.convert(text)

    assert result == (
        "ami ajke [UNKNOWN:খুব] office e jabo"
    )


def test_unknown_word_detection():
    text = "আমি আজকে খুব সুন্দর অফিসে যাব"

    result, unknown_words = (
        converter.convert_with_unknowns(text)
    )

    assert result == (
        "ami ajke [UNKNOWN:খুব] "
        "[UNKNOWN:সুন্দর] office e jabo"
    )

    assert unknown_words == [
        "খুব",
        "সুন্দর",
    ]


def test_empty_text():
    assert converter.convert("") == ""