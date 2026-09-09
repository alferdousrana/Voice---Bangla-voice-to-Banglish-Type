import time

import numpy as np

from app.audio.stream_recorder import StreamingRecorder


def main():
    recorder = StreamingRecorder(
        sample_rate=16000,
        device=2,
        chunk_duration=0.5,
    )

    recorder.start()

    print()
    print("Speak for 10 seconds...")
    print("Press Ctrl+C to stop.")
    print()

    start_time = time.time()
    chunk_number = 0

    try:
        while time.time() - start_time < 10:
            chunk = recorder.get_chunk()

            if chunk is None:
                continue

            chunk_number += 1

            rms = np.sqrt(np.mean(chunk ** 2))
            peak = np.max(np.abs(chunk))

            print(
                f"Chunk {chunk_number:02d} | "
                f"Samples: {len(chunk)} | "
                f"RMS: {rms:.4f} | "
                f"Peak: {peak:.4f}"
            )

    except KeyboardInterrupt:
        print("\nStopped by user.")

    finally:
        recorder.stop()

    print()
    print(f"Total chunks: {chunk_number}")


if __name__ == "__main__":
    main()