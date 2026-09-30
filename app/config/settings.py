import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
SETTINGS_FILE = DATA_DIR / "settings.json"

SAMPLE_RATE = 16000
CHANNELS = 1


DEFAULT_SETTINGS = {
    "audio_device": 17,
}


def _ensure_settings_file():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not SETTINGS_FILE.exists():
        with open(
            SETTINGS_FILE,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                DEFAULT_SETTINGS,
                file,
                ensure_ascii=False,
                indent=4,
            )


def load_settings():
    _ensure_settings_file()

    try:
        with open(
            SETTINGS_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if isinstance(data, dict):
            return data

    except (
        json.JSONDecodeError,
        OSError,
    ):
        pass

    return dict(DEFAULT_SETTINGS)


def save_settings(settings):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(
        SETTINGS_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            settings,
            file,
            ensure_ascii=False,
            indent=4,
        )


def get_audio_device():
    settings = load_settings()

    return settings.get(
        "audio_device",
        DEFAULT_SETTINGS["audio_device"],
    )


def set_audio_device(device_index):
    settings = load_settings()

    settings["audio_device"] = int(
        device_index
    )

    save_settings(settings)