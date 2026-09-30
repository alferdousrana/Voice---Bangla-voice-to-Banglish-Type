import numpy as np
import sounddevice as sd

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from app.config.settings import (
    CHANNELS,
    SAMPLE_RATE,
    get_audio_device,
    set_audio_device,
)


class MicrophoneWindow(QWidget):

    # Sent when user clicks "Save & Start Voice"
    # and microphone is successfully validated.
    start_requested = Signal(int)

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Voice — Microphone Settings"
        )

        self.resize(650, 430)

        # -----------------------------------------
        # STATE
        # -----------------------------------------

        self.devices = []

        self.test_stream = None
        self.testing = False

        self._current_level = 0

        # -----------------------------------------
        # LEVEL TIMER
        # -----------------------------------------

        self.level_timer = QTimer(self)

        self.level_timer.timeout.connect(
            self.update_input_level
        )

        # -----------------------------------------
        # UI
        # -----------------------------------------

        self.setup_ui()

        # -----------------------------------------
        # LOAD DEVICES
        # -----------------------------------------

        self.load_microphones()

    # =================================================
    # UI
    # =================================================

    def setup_ui(self):

        layout = QVBoxLayout(self)

        layout.setSpacing(12)

        # -----------------------------------------
        # TITLE
        # -----------------------------------------

        title = QLabel(
            "🎙️ Select Microphone"
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 24px;
                font-weight: bold;
                padding: 8px;
            }
            """
        )

        layout.addWidget(title)

        # -----------------------------------------
        # DESCRIPTION
        # -----------------------------------------

        description = QLabel(
            "Choose the microphone Voice should "
            "listen to. Only the selected input "
            "device will be used."
        )

        description.setWordWrap(True)

        description.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                padding-bottom: 5px;
            }
            """
        )

        layout.addWidget(description)

        # -----------------------------------------
        # MICROPHONE LABEL
        # -----------------------------------------

        microphone_label = QLabel(
            "🎤 Microphone"
        )

        microphone_label.setStyleSheet(
            "font-weight: bold;"
        )

        layout.addWidget(
            microphone_label
        )

        # -----------------------------------------
        # MICROPHONE COMBO
        # -----------------------------------------

        self.microphone_combo = QComboBox()

        self.microphone_combo.setMinimumHeight(
            38
        )

        layout.addWidget(
            self.microphone_combo
        )

        # -----------------------------------------
        # INPUT LEVEL
        # -----------------------------------------

        level_label = QLabel(
            "📊 Input Level"
        )

        level_label.setStyleSheet(
            "font-weight: bold;"
        )

        layout.addWidget(
            level_label
        )

        self.level_bar = QProgressBar()

        self.level_bar.setRange(
            0,
            100,
        )

        self.level_bar.setValue(0)

        self.level_bar.setTextVisible(True)

        self.level_bar.setFormat(
            "%p%"
        )

        layout.addWidget(
            self.level_bar
        )

        # -----------------------------------------
        # STATUS
        # -----------------------------------------

        self.status_label = QLabel(
            "Ready."
        )

        self.status_label.setWordWrap(True)

        self.status_label.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                padding: 5px;
            }
            """
        )

        layout.addWidget(
            self.status_label
        )

        # -----------------------------------------
        # BUTTONS
        # -----------------------------------------

        button_layout = QHBoxLayout()

        # Test
        self.test_button = QPushButton(
            "🎤 Test Microphone"
        )

        self.test_button.setMinimumHeight(
            40
        )

        self.test_button.clicked.connect(
            self.toggle_microphone_test
        )

        button_layout.addWidget(
            self.test_button
        )

        # Refresh
        self.refresh_button = QPushButton(
            "🔄 Refresh"
        )

        self.refresh_button.setMinimumHeight(
            40
        )

        self.refresh_button.clicked.connect(
            self.load_microphones
        )

        button_layout.addWidget(
            self.refresh_button
        )

        layout.addLayout(
            button_layout
        )

        # -----------------------------------------
        # START VOICE
        # -----------------------------------------

        self.start_button = QPushButton(
            "🚀 Save & Start Voice"
        )

        self.start_button.setMinimumHeight(
            48
        )

        self.start_button.setStyleSheet(
            """
            QPushButton {
                font-size: 15px;
                font-weight: bold;
                padding: 8px;
            }
            """
        )

        self.start_button.clicked.connect(
            self.save_and_start
        )

        layout.addWidget(
            self.start_button
        )

    # =================================================
    # LOAD MICROPHONES
    # =================================================

    def load_microphones(self):

        self.stop_microphone_test()

        self.microphone_combo.clear()

        self.devices = []

        try:

            devices = sd.query_devices()

            saved_device = get_audio_device()

            saved_combo_index = -1

            for index, device in enumerate(
                devices
            ):

                # Only input devices.
                input_channels = int(
                    device[
                        "max_input_channels"
                    ]
                )

                if input_channels < 1:
                    continue

                name = str(
                    device["name"]
                )

                display_name = (
                    f"{name} "
                    f"(ID: {index})"
                )

                self.devices.append(
                    index
                )

                self.microphone_combo.addItem(
                    display_name,
                    index,
                )

                # Remember saved microphone.
                if index == saved_device:

                    saved_combo_index = (
                        self.microphone_combo.count()
                        - 1
                    )

            # -----------------------------------------
            # RESTORE SAVED DEVICE
            # -----------------------------------------

            if saved_combo_index >= 0:

                self.microphone_combo.setCurrentIndex(
                    saved_combo_index
                )

            elif self.microphone_combo.count():

                self.microphone_combo.setCurrentIndex(
                    0
                )

            # -----------------------------------------
            # STATUS
            # -----------------------------------------

            count = (
                self.microphone_combo.count()
            )

            if count:

                self.status_label.setText(
                    f"🎙️ {count} microphone(s) available."
                )

            else:

                self.status_label.setText(
                    "❌ No microphone found."
                )

        except Exception as exc:

            self.status_label.setText(
                f"❌ Failed to load microphones: {exc}"
            )

    # =================================================
    # SELECTED DEVICE
    # =================================================

    def selected_device(self):

        device = (
            self.microphone_combo.currentData()
        )

        if device is None:
            return None

        return int(device)

    # =================================================
    # TEST MICROPHONE
    # =================================================

    def toggle_microphone_test(self):

        if self.testing:

            self.stop_microphone_test()

        else:

            self.start_microphone_test()

    def start_microphone_test(self):

        device = self.selected_device()

        if device is None:

            QMessageBox.warning(
                self,
                "No Microphone",
                "Please select a microphone first.",
            )

            return

        try:

            # -----------------------------------------
            # VALIDATE DEVICE
            # -----------------------------------------

            sd.check_input_settings(
                device=device,
                channels=CHANNELS,
                samplerate=SAMPLE_RATE,
                dtype="float32",
            )

            device_info = sd.query_devices(
                device
            )

            device_name = device_info[
                "name"
            ]

            # -----------------------------------------
            # RESET LEVEL
            # -----------------------------------------

            self._current_level = 0

            self.level_bar.setValue(
                0
            )

            # -----------------------------------------
            # CREATE TEST STREAM
            # -----------------------------------------

            self.test_stream = sd.InputStream(
                device=device,
                channels=CHANNELS,
                samplerate=SAMPLE_RATE,
                dtype="float32",
                blocksize=512,
                callback=self.audio_callback,
            )

            self.test_stream.start()

            self.testing = True

            # -----------------------------------------
            # UI
            # -----------------------------------------

            self.test_button.setText(
                "⏹️ Stop Test"
            )

            self.refresh_button.setEnabled(
                False
            )

            self.microphone_combo.setEnabled(
                False
            )

            self.status_label.setText(
                f"🟢 Testing: {device_name}\n"
                "Speak now..."
            )

            self.level_timer.start(
                100
            )

        except Exception as exc:

            self.test_stream = None
            self.testing = False

            QMessageBox.critical(
                self,
                "Microphone Error",
                str(exc),
            )

    # =================================================
    # AUDIO CALLBACK
    # =================================================

    def audio_callback(
        self,
        indata,
        frames,
        time,
        status,
    ):

        if status:
            return

        if not self.testing:
            return

        if len(indata) == 0:
            return

        try:

            audio = indata[:, 0]

            # RMS volume.
            rms = float(
                np.sqrt(
                    np.mean(
                        audio * audio
                    )
                )
            )

            # Convert to UI level.
            level = min(
                100,
                int(rms * 500),
            )

            self._current_level = level

        except Exception:
            self._current_level = 0

    # =================================================
    # UPDATE INPUT LEVEL
    # =================================================

    def update_input_level(self):

        level = getattr(
            self,
            "_current_level",
            0,
        )

        self.level_bar.setValue(
            level
        )

    # =================================================
    # STOP MICROPHONE TEST
    # =================================================

    def stop_microphone_test(self):

        self.level_timer.stop()

        if self.test_stream is not None:

            try:

                self.test_stream.stop()

            except Exception:
                pass

            try:

                self.test_stream.close()

            except Exception:
                pass

            self.test_stream = None

        self.testing = False

        self._current_level = 0

        self.level_bar.setValue(
            0
        )

        self.test_button.setText(
            "🎤 Test Microphone"
        )

        self.refresh_button.setEnabled(
            True
        )

        self.microphone_combo.setEnabled(
            True
        )

    # =================================================
    # SAVE & START
    # =================================================

    def save_and_start(self):

        device = self.selected_device()

        if device is None:

            QMessageBox.warning(
                self,
                "No Microphone",
                "Please select a microphone.",
            )

            return

        try:

            # -----------------------------------------
            # VALIDATE AGAIN
            # -----------------------------------------

            sd.check_input_settings(
                device=device,
                channels=CHANNELS,
                samplerate=SAMPLE_RATE,
                dtype="float32",
            )

            # -----------------------------------------
            # SAVE DEVICE
            # -----------------------------------------

            set_audio_device(
                device
            )

            device_info = sd.query_devices(
                device
            )

            device_name = device_info[
                "name"
            ]

            # -----------------------------------------
            # STOP TEST
            # -----------------------------------------

            self.stop_microphone_test()

            # -----------------------------------------
            # STATUS
            # -----------------------------------------

            self.status_label.setText(
                f"✅ Microphone saved:\n"
                f"{device_name}"
            )

            print(
                f"🎙️ Selected microphone: "
                f"{device_name}"
            )

            print(
                f"🎧 Input Device ID: "
                f"{device}"
            )

            # -----------------------------------------
            # TELL MAIN APP TO START
            # -----------------------------------------

            self.start_requested.emit(
                device
            )

            # -----------------------------------------
            # CLOSE WINDOW
            # -----------------------------------------

            self.close()

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Microphone Error",
                str(exc),
            )

    # =================================================
    # CLOSE EVENT
    # =================================================

    def closeEvent(self, event):

        self.stop_microphone_test()

        event.accept()