import queue

import sounddevice as sd

from app.config.settings import (
    CHANNELS,
    SAMPLE_RATE,
    get_audio_device,
)


class StreamingRecorder:

    def __init__(
        self,
        sample_rate=SAMPLE_RATE,
        channels=CHANNELS,
        device=None,
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

    # -----------------------------------------
    # AUDIO CALLBACK
    # -----------------------------------------

    def _audio_callback(
        self,
        indata,
        frames,
        time,
        status,
    ):
        if status:
            print(
                f"⚠️ Audio status: {status}"
            )

        if not self.running:
            return

        # Mono input
        audio = indata[:, 0].copy()

        self.audio_queue.put(audio)

    # -----------------------------------------
    # START
    # -----------------------------------------

    def start(self):

        if self.running:
            return

        # If no device was explicitly supplied,
        # use the saved microphone from settings.
        if self.device is None:
            self.device = get_audio_device()

        if self.device is None:
            raise RuntimeError(
                "No microphone device selected."
            )

        # Validate selected input device
        try:

            sd.check_input_settings(
                device=self.device,
                channels=self.channels,
                samplerate=self.sample_rate,
                dtype="float32",
            )

        except Exception as exc:

            raise RuntimeError(
                f"Selected microphone cannot be used: "
                f"{exc}"
            ) from exc

        # Get device information
        try:

            device_info = sd.query_devices(
                self.device
            )

            device_name = device_info[
                "name"
            ]

        except Exception:

            device_name = (
                f"Device {self.device}"
            )

        print(
            f"🎙️ Microphone: {device_name}"
        )

        print(
            f"🎧 Input Device ID: {self.device}"
        )

        print(
            f"🎚️ Sample Rate: "
            f"{self.sample_rate} Hz"
        )

        print(
            f"🔊 Channels: "
            f"{self.channels}"
        )

        # -------------------------------------
        # CREATE STREAM
        # -------------------------------------

        try:

            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="float32",
                device=self.device,
                blocksize=self.chunk_size,
                callback=self._audio_callback,
            )

            self.stream.start()

            self.running = True

            print(
                "🎙️ Streaming recorder started."
            )

            print(
                "🎤 Listening only to selected microphone."
            )

        except Exception as exc:

            self.stream = None
            self.running = False

            raise RuntimeError(
                f"Failed to start microphone: "
                f"{exc}"
            ) from exc

    # -----------------------------------------
    # GET AUDIO CHUNK
    # -----------------------------------------

    def get_chunk(
        self,
        timeout=1,
    ):

        if not self.running:
            return None

        try:

            return self.audio_queue.get(
                timeout=timeout
            )

        except queue.Empty:

            return None

    # -----------------------------------------
    # STOP
    # -----------------------------------------

    def stop(self):

        if not self.running and self.stream is None:
            return

        self.running = False

        if self.stream is not None:

            try:
                self.stream.stop()

            except Exception:
                pass

            try:
                self.stream.close()

            except Exception:
                pass

            self.stream = None

        self.clear_queue()

        print(
            "🛑 Streaming recorder stopped."
        )

    # -----------------------------------------
    # CLEAR QUEUE
    # -----------------------------------------

    def clear_queue(self):

        while True:

            try:

                self.audio_queue.get_nowait()

            except queue.Empty:

                break

    # -----------------------------------------
    # DEVICE INFO
    # -----------------------------------------

    def get_device_info(self):

        if self.device is None:
            return None

        try:

            return sd.query_devices(
                self.device
            )

        except Exception:

            return None

    # -----------------------------------------
    # DEVICE NAME
    # -----------------------------------------

    def get_device_name(self):

        device_info = (
            self.get_device_info()
        )

        if device_info is None:
            return "Unknown microphone"

        return device_info[
            "name"
        ]