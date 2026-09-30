from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.transliteration.dictionary_manager import DictionaryManager
from app.transliteration.unknown_words import (
    load_unknown_words,
    remove_unknown_word,
)


class DictionaryWindow(QWidget):

    word_added = Signal(str, str)
    phrase_added = Signal(str, str)

    # Voice listening control signals
    start_listening_requested = Signal()
    stop_listening_requested = Signal()

    # Emitted when user closes the window
    window_closed = Signal()

    def __init__(self):
        super().__init__()

        self.dictionary = DictionaryManager()

        self.listening = True

        self.setWindowTitle("Voice — Banglish Dictionary")
        self.resize(700, 600)

        self.setup_ui()
        self.refresh_unknown_words()

        # Voice starts automatically when this window opens.
        self.update_listening_button()

    def setup_ui(self):

        layout = QVBoxLayout(self)

        # -------------------------
        # TITLE
        # -------------------------

        title = QLabel("🔤 Voice — Banglish Dictionary")
        title.setStyleSheet(
            """
            QLabel {
                font-size: 22px;
                font-weight: bold;
                padding: 8px;
            }
            """
        )

        layout.addWidget(title)

        description = QLabel(
            "Unknown Bangla words detected by Voice. "
            "Select a word, correct its Banglish spelling, "
            "and save it to your personal dictionary."
        )

        description.setWordWrap(True)
        layout.addWidget(description)

        # -------------------------
        # UNKNOWN WORDS
        # -------------------------

        unknown_label = QLabel("🆕 Unknown Words")

        unknown_label.setStyleSheet(
            "font-size: 16px; font-weight: bold;"
        )

        layout.addWidget(unknown_label)

        self.unknown_list = QListWidget()

        self.unknown_list.itemClicked.connect(
            self.select_unknown_word
        )

        layout.addWidget(self.unknown_list)

        # -------------------------
        # TYPE
        # -------------------------

        type_layout = QHBoxLayout()

        type_layout.addWidget(
            QLabel("Type:")
        )

        self.type_combo = QComboBox()

        self.type_combo.addItems(
            [
                "Word",
                "Phrase",
            ]
        )

        type_layout.addWidget(
            self.type_combo
        )

        layout.addLayout(type_layout)

        # -------------------------
        # BANGLA
        # -------------------------

        layout.addWidget(
            QLabel("Bangla Word / Phrase")
        )

        self.bangla_input = QLineEdit()

        self.bangla_input.setPlaceholderText(
            "Example: আজকের"
        )

        layout.addWidget(
            self.bangla_input
        )

        # -------------------------
        # BANGLISH
        # -------------------------

        layout.addWidget(
            QLabel("Correct Banglish")
        )

        self.banglish_input = QLineEdit()

        self.banglish_input.setPlaceholderText(
            "Example: ajker"
        )

        layout.addWidget(
            self.banglish_input
        )

        # -------------------------
        # DICTIONARY BUTTONS
        # -------------------------

        button_layout = QHBoxLayout()

        self.add_button = QPushButton(
            "➕ Add to Dictionary"
        )

        self.add_button.clicked.connect(
            self.add_to_dictionary
        )

        button_layout.addWidget(
            self.add_button
        )

        self.delete_button = QPushButton(
            "🗑️ Remove Unknown"
        )

        self.delete_button.clicked.connect(
            self.delete_unknown
        )

        button_layout.addWidget(
            self.delete_button
        )

        layout.addLayout(
            button_layout
        )

        # -------------------------
        # VOICE CONTROL
        # -------------------------

        voice_control_layout = QHBoxLayout()

        self.listening_button = QPushButton()

        self.listening_button.setMinimumHeight(42)

        self.listening_button.clicked.connect(
            self.toggle_listening
        )

        voice_control_layout.addWidget(
            self.listening_button
        )

        layout.addLayout(
            voice_control_layout
        )

        # -------------------------
        # STATUS
        # -------------------------

        self.status_label = QLabel(
            "Ready."
        )

        layout.addWidget(
            self.status_label
        )

    # =====================================================
    # LISTENING CONTROL
    # =====================================================

    def toggle_listening(self):

        if self.listening:

            self.listening = False

            self.update_listening_button()

            self.status_label.setText(
                "⚪ LISTENING STOPPED"
            )

            self.stop_listening_requested.emit()

        else:

            self.listening = True

            self.update_listening_button()

            self.status_label.setText(
                "🔴 STARTING LISTENING..."
            )

            self.start_listening_requested.emit()

    def update_listening_button(self):

        if self.listening:

            self.listening_button.setText(
                "⏹ Stop Listening"
            )

        else:

            self.listening_button.setText(
                "🎙️ Start Listening"
            )

    def set_listening_state(self, listening):

        self.listening = bool(listening)

        self.update_listening_button()

    # =====================================================
    # UNKNOWN WORDS
    # =====================================================

    def refresh_unknown_words(self):

        self.unknown_list.clear()

        unknown_words = load_unknown_words()

        for word in unknown_words:

            item = QListWidgetItem(word)

            self.unknown_list.addItem(
                item
            )

        if self.listening:

            self.status_label.setText(
                f"📝 {len(unknown_words)} unknown word(s)"
            )

    def select_unknown_word(self, item):

        word = item.text()

        self.bangla_input.setText(
            word
        )

        self.banglish_input.clear()

        self.type_combo.setCurrentText(
            "Word"
        )

        self.banglish_input.setFocus()

    # =====================================================
    # ADD TO DICTIONARY
    # =====================================================

    def add_to_dictionary(self):

        bangla = (
            self.bangla_input
            .text()
            .strip()
        )

        banglish = (
            self.banglish_input
            .text()
            .strip()
        )

        dictionary_type = (
            self.type_combo.currentText()
        )

        if not bangla:

            QMessageBox.warning(
                self,
                "Missing Text",
                "Please enter a Bangla word or phrase.",
            )

            return

        if not banglish:

            QMessageBox.warning(
                self,
                "Missing Banglish",
                "Please enter the correct Banglish.",
            )

            return

        if dictionary_type == "Word":

            success = self.dictionary.add_word(
                bangla,
                banglish,
            )

            if not success:
                return

            remove_unknown_word(
                bangla
            )

            self.word_added.emit(
                bangla,
                banglish,
            )

        else:

            success = self.dictionary.add_phrase(
                bangla,
                banglish,
            )

            if not success:
                return

            remove_unknown_word(
                bangla
            )

            self.phrase_added.emit(
                bangla,
                banglish,
            )

        self.bangla_input.clear()
        self.banglish_input.clear()

        self.refresh_unknown_words()

        self.status_label.setText(
            f"✅ Added: {bangla} → {banglish}"
        )

    # =====================================================
    # DELETE UNKNOWN
    # =====================================================

    def delete_unknown(self):

        current_item = (
            self.unknown_list.currentItem()
        )

        if current_item is None:
            return

        word = current_item.text()

        remove_unknown_word(
            word
        )

        self.refresh_unknown_words()

    # =====================================================
    # CLOSE WINDOW
    # =====================================================

    def closeEvent(self, event):

        self.window_closed.emit()

        event.accept()


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    from PySide6.QtWidgets import QApplication

    app = QApplication([])

    window = DictionaryWindow()
    window.show()

    app.exec()