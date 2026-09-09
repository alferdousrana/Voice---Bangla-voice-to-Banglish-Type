import queue
import threading

import numpy as np
import sounddevice as sd


class StreamingRecorder:
    def __init__(
        self,
        sample_rate=16000,
        channels=1,
        device=2,
        chunk_duration=0.032,
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.device = device
        self.chunk_duration = chunk_duration

        self.chunk_size = int(
            self.sample_rate * self.chunk_duration
        )

        self.audio_queue = queue.Queue()

        self.stream = None
        self.running = False

    def _audio_callback(self, indata, frames, time, status):
        if status:
            print(f"Audio status: {status}")

        audio = indata[:, 0].copy()

        self.audio_queue.put(audio)

    def start(self):
        if self.running:
            return

        self.running = True

        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            device=self.device,
            blocksize=self.chunk_size,
            callback=self._audio_callback,
        )

        self.stream.start()

        print("🎙️ Streaming recorder started.")

    def get_chunk(self, timeout=1):
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def stop(self):
        if not self.running:
            return

        self.running = False

        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        print("🛑 Streaming recorder stopped.")

    def clear_queue(self):
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break