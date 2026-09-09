import os
import time

import numpy as np
from scipy.io import wavfile

from app.speech.fast_recognizer import FastBanglaRecognizer


AUDIO_DIR = "benchmark_audio"

EXPECTED = [
    "আমি আজকে অফিসে যাব না।",
    "ভাই কালকে প্রজেক্টটা শেষ করে দিও।",
    "আমার মোবাইলটা ভেঙে গেছে।",
    "তুমি এখন কোথায় আছো?",
    "বাসায় গিয়ে আমাকে ফোন দিও।",
    "আমি আজকে একটু দেরি করে আসবো।",
    "কাল সকালে আমাদের মিটিং আছে।",
    "তুমি কি আমাকে এই কাজটা বুঝিয়ে দিতে পারবে?",
    "আমি এখন কম্পিউটারে কাজ করছি।",
    "আজকে রাতে বাসায় গিয়ে প্রজেক্টের কাজ শেষ করবো।",
]


def normalize(text):
    text = text.strip()

    for char in "।.,?!":
        text = text.replace(char, "")

    return " ".join(text.split())


def load_audio(path):
    sample_rate, audio = wavfile.read(path)

    audio = np.asarray(audio)

    if audio.dtype == np.int16:
        audio = audio.astype(np.float32) / 32768.0
    elif audio.dtype == np.int32:
        audio = audio.astype(np.float32) / 2147483648.0
    else:
        audio = audio.astype(np.float32)

    if audio.ndim > 1:
        audio = audio[:, 0]

    audio = np.clip(audio, -1.0, 1.0)

    return sample_rate, audio


def main():
    print("=" * 70)
    print("🚀 FAST BENGALI ASR — SAVED AUDIO BENCHMARK")
    print("=" * 70)

    print("\n🧠 Loading FastConformer...")
    recognizer = FastBanglaRecognizer()

    results = []

    print("\n" + "=" * 70)
    print("🎵 PROCESSING SAVED RECORDINGS")
    print("=" * 70)

    for index, expected in enumerate(EXPECTED, start=1):

        audio_path = os.path.join(
            AUDIO_DIR,
            f"sentence_{index:02d}.wav",
        )

        if not os.path.exists(audio_path):
            print(f"\n⚠️ Missing: {audio_path}")
            continue

        print("\n" + "-" * 70)
        print(f"🎙️ Sentence {index}/10")
        print(f"📁 File: {audio_path}")

        sample_rate, audio = load_audio(audio_path)

        duration = len(audio) / sample_rate

        print(f"⏱️ Audio duration: {duration:.2f}s")

        start = time.time()

        recognized = recognizer.transcribe(
            audio,
            sample_rate,
        )

        elapsed = time.time() - start

        rtf = elapsed / duration if duration > 0 else 0

        expected_normalized = normalize(expected)
        recognized_normalized = normalize(recognized)

        exact_match = (
            expected_normalized == recognized_normalized
        )

        results.append(
            {
                "index": index,
                "expected": expected,
                "recognized": recognized,
                "duration": duration,
                "time": elapsed,
                "rtf": rtf,
                "match": exact_match,
            }
        )

        print("\n🇧🇩 RESULT")
        print(f"Expected  : {expected}")
        print(f"Recognized: {recognized}")
        print(f"Match     : {'✅' if exact_match else '❌'}")
        print(f"STT time  : {elapsed:.2f}s")
        print(f"RTF       : {rtf:.2f}x")

    if not results:
        print("\n❌ No audio files found.")
        return

    print("\n\n")
    print("=" * 70)
    print("📊 FINAL RESULTS")
    print("=" * 70)

    matches = sum(
        1 for result in results
        if result["match"]
    )

    total_duration = sum(
        result["duration"]
        for result in results
    )

    total_time = sum(
        result["time"]
        for result in results
    )

    for result in results:
        status = "✅" if result["match"] else "❌"

        print(
            f"{result['index']:02d}. "
            f"{status} "
            f"{result['time']:.2f}s "
            f"| RTF {result['rtf']:.2f}x "
            f"| {result['recognized']}"
        )

    accuracy = (matches / len(results)) * 100

    print("\n" + "-" * 70)

    print(
        f"Exact sentence match : "
        f"{matches}/{len(results)}"
    )

    print(
        f"Exact match accuracy : "
        f"{accuracy:.1f}%"
    )

    print(
        f"Total audio duration : "
        f"{total_duration:.2f}s"
    )

    print(
        f"Total STT time       : "
        f"{total_time:.2f}s"
    )

    if total_duration > 0:
        print(
            f"Overall RTF          : "
            f"{total_time / total_duration:.2f}x"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()