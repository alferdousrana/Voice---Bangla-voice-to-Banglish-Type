# app/transliteration/converter.py

import re

from .dictionary import (
    CUSTOM_PHRASES,
    CUSTOM_WORDS,
    WORD_MAP,
)


# ============================================================
# TOKEN PATTERNS
# ============================================================

BENGALI_WORD_PATTERN = r"[\u0980-\u09FF]+"

TOKEN_PATTERN = (
    r"[\u0980-\u09FF]+"
    r"|[A-Za-z0-9]+"
    r"|[^\w\s]"
    r"|\s+"
)


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_bangla(text: str) -> str:
    """
    Normalize common Bengali Unicode variants.
    """

    if not text:
        return ""

    replacements = {
        "য়": "য়",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.strip()


# ============================================================
# DICTIONARY LOOKUP
# ============================================================

def lookup_word(word: str):
    """
    Look up a Bengali word.

    Priority:

        1. CUSTOM_WORDS
        2. WORD_MAP

    Returns:
        Banglish string if found
        None if unknown
    """

    word = normalize_bangla(word)

    # User's custom dictionary has highest priority.
    if word in CUSTOM_WORDS:
        return CUSTOM_WORDS[word]

    # Common dictionary.
    if word in WORD_MAP:
        return WORD_MAP[word]

    return None


# ============================================================
# CUSTOM PHRASES
# ============================================================

def apply_custom_phrases(text: str):
    """
    Replace known phrases before word-level conversion.

    Longer phrases are matched first.
    """

    if not text:
        return text, []

    matched_phrases = []

    phrases = sorted(
        CUSTOM_PHRASES.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )

    for bangla_phrase, banglish_phrase in phrases:

        if bangla_phrase in text:

            text = text.replace(
                bangla_phrase,
                banglish_phrase,
            )

            matched_phrases.append(
                bangla_phrase
            )

    return text, matched_phrases


# ============================================================
# MAIN CONVERTER
# ============================================================

def bangla_to_banglish(
    text: str,
    show_unknown=False,
):
    """
    Convert Bengali text using dictionary only.

    Unknown Bengali words are NOT transliterated.

    Example:

        আমি আজকে অফিসে যাব না

    becomes:

        ami ajke office e jabo na

    Unknown words are reported separately.
    """

    if not text:
        if show_unknown:
            return "", []

        return ""

    text = normalize_bangla(text)

    # --------------------------------------------------------
    # Apply custom phrases first
    # --------------------------------------------------------

    text, matched_phrases = apply_custom_phrases(text)

    # --------------------------------------------------------
    # Tokenize
    # --------------------------------------------------------

    tokens = re.findall(
        TOKEN_PATTERN,
        text,
        flags=re.UNICODE,
    )

    result = []
    unknown_words = []

    for token in tokens:

        # ----------------------------------------------------
        # Bengali word
        # ----------------------------------------------------

        if re.fullmatch(
            BENGALI_WORD_PATTERN,
            token,
        ):

            converted = lookup_word(token)

            if converted is not None:

                result.append(converted)

            else:

                # Do NOT use fallback transliteration.
                result.append(
                    f"[UNKNOWN:{token}]"
                )

                if token not in unknown_words:
                    unknown_words.append(token)

        # ----------------------------------------------------
        # Whitespace
        # ----------------------------------------------------

        elif token.isspace():

            result.append(token)

        # ----------------------------------------------------
        # English / numbers / punctuation
        # ----------------------------------------------------

        else:

            result.append(token)

    # --------------------------------------------------------
    # Build output
    # --------------------------------------------------------

    output = "".join(result)

    output = re.sub(
        r"[ \t]+",
        " ",
        output,
    )

    output = output.strip()

    # --------------------------------------------------------
    # Console warning
    # --------------------------------------------------------

    if unknown_words:
        print(
            "⚠️ Unknown words: "
            + ", ".join(unknown_words)
        )

    if show_unknown:
        return output, unknown_words

    return output


# ============================================================
# CLASS API
# ============================================================

class BanglishConverter:
    """
    Main Banglish converter.

    Example:

        converter = BanglishConverter()

        text = converter.convert(
            "আমি আজকে অফিসে যাব না"
        )
    """

    def convert(self, text: str) -> str:
        return bangla_to_banglish(text)

    def convert_with_unknowns(self, text: str):
        """
        Return both converted text and unknown words.

        Example:

            result, unknowns = converter.convert_with_unknowns(
                "আমি আজকে খুব অফিসে যাব"
            )
        """

        return bangla_to_banglish(
            text,
            show_unknown=True,
        )