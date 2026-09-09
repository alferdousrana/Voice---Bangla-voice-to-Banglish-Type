# app/transliteration/dictionary.py


# ============================================================
# CUSTOM PHRASES
# ============================================================
# এখানে নিজের preferred Banglish phrase যোগ করতে পারবে।
#
# IMPORTANT:
# Longer phrases should come before shorter phrases.
# The converter automatically handles this by sorting by length.
# ============================================================

CUSTOM_PHRASES = {
    "শেষ করে দিও": "sesh kore dio",
    "করে দিও": "kore dio",
    "একটু পরে": "ektu pore",
    "এখন কোথায়": "ekhon kothay",
}


# ============================================================
# CUSTOM WORDS
# ============================================================
# নিজের Banglish style এখানে রাখবে।
#
# Example:
# "করতেছি": "kortesi"
# "হইছে": "hoise"
# ============================================================

CUSTOM_WORDS = {
    "করতেছি": "kortesi",
    "করতেছে": "kortese",
    "যাইতেছি": "jaitesi",
    "যাইতেছে": "jaitese",
    "আসতেছি": "astesi",
    "আসতেছে": "astese",
    "হইছে": "hoise",
    "হইতেছে": "hoitese",
}


# ============================================================
# COMMON WORDS
# ============================================================

WORD_MAP = {
    "আমি": "ami",
    "আমার": "amar",
    "আমাকে": "amake",
    "আমাদের": "amader",

    "তুমি": "tumi",
    "তোমার": "tomar",
    "তোমাকে": "tomake",

    "ভাই": "bhai",
    "না": "na",
    "হ্যাঁ": "hya",

    # Time
    "আজ": "aj",
    "আজকে": "ajke",
    "কাল": "kal",
    "কালকে": "kalke",
    "এখন": "ekhon",
    "সকালে": "sokale",
    "রাতে": "rate",

    # Places
    "অফিস": "office",
    "অফিসে": "office e",
    "বাসা": "basha",
    "বাসায়": "basay",
    "বাসায়": "basay",

    # Verbs
    "যাব": "jabo",
    "যাবে": "jabe",
    "যাই": "jai",
    "যাচ্ছি": "jacchi",

    "আসব": "asbo",
    "আসবো": "asbo",
    "আসবে": "asbe",
    "আসছি": "aschi",

    "করে": "kore",
    "কর": "koro",
    "করো": "koro",
    "করছি": "korchi",
    "করব": "korbo",
    "করবো": "korbo",

    "গেছে": "geche",
    "গিয়ে": "giye",
    "গিয়ে": "giye",
    "যেতে": "jete",

    "দিও": "dio",
    "দাও": "dao",
    "দিতে": "dite",

    # Work / Project
    "প্রজেক্ট": "project",
    "প্রজেক্টটা": "project ta",
    "প্রজেক্টের": "project er",
    "কাজ": "kaj",
    "কাজটা": "kajta",
    "শেষ": "sesh",

    "মিটিং": "meeting",
    "আছে": "ache",

    # Device
    "মোবাইল": "mobile",
    "মোবাইলটা": "mobile ta",
    "ফোন": "phone",

    "কম্পিউটার": "computer",
    "কম্পিউটারে": "computer e",

    # Common
    "একটু": "ektu",
    "দেরি": "deri",

    "কোথায়": "kothay",
    "কোথায়": "kothay",

    "আছো": "acho",
    "কি": "ki",
    "এই": "ei",

    "বুঝিয়ে": "bujhiye",
    "বুঝিয়ে": "bujhiye",

    "পারবে": "parbe",

    "ফোন": "phone",
    "গিয়ে": "giye",
    "গিয়ে": "giye",
    
    # Bengali postpositions (VERY IMPORTANT)
    "এ": "e",
    "তে": "te",
    "এর": "er",
    "র": "r",
    "কে": "ke",
    "টা": "ta",
    "টি": "ti",
    "গুলো": "gulo",
    "গুলি": "guli",
    "দের": "der",
    "ভাবে": "vabe",
    "দিকে": "dike",
    "পর": "por",
    "পরে": "pore",
    "সাথে": "sathe",

    # Common Banglish / technical words
    "ডেভেলপমেন্ট": "development",
    "ডেভেলপার": "developer",
    "ব্যাকএন্ড": "backend",
    "ফ্রন্টএন্ড": "frontend",
    "জ্যাঙ্গো": "django",
    "রিয়েক্ট": "react",
    "রিয়েক্ট": "react",
    "গিটহাব": "github",

    # Other
    "ভেঙে": "venge",
    "ভেঙ্গে": "venge",
}