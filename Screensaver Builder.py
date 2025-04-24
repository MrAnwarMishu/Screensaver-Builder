from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QLineEdit, QTextEdit
)
from PyQt5.QtGui import QMovie, QIcon, QPainter, QColor, QPixmap, QRegExpValidator
from PyQt5.QtCore import Qt, QTimer, QPoint, QRegExp

class CircularProgress(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 120)
        self.progress_value = 0
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def setProgress(self, value):
        self.progress_value = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(10, 10, -10, -10)
        painter.setPen(QColor(200, 200, 200))
        painter.setBrush(Qt.transparent)
        painter.drawEllipse(rect)

        pen = painter.pen()
        pen.setWidth(6)
        pen.setColor(QColor(76, 175, 80))
        painter.setPen(pen)
        painter.drawArc(rect, 90 * 16, -self.progress_value * 360 * 16 // 100)

        painter.setPen(QColor(0, 0, 0))
        if self.progress_value < 100:
            painter.drawText(self.rect(), Qt.AlignCenter, f"{self.progress_value}%")
        else:
            painter.drawText(self.rect(), Qt.AlignCenter, "✅")

class GifToScrBuilder(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screensaver Builder")
        self.setWindowIcon(QIcon("icon.png"))
        self.setFixedSize(600, 500)
        self.init_ui()
        self.gif_path = None
        self.sound_path = None
        self.icon_path = None
        self.sound_enabled = False

    def init_ui(self):
        layout = QVBoxLayout()

        self.preview_label = QLabel("Screen Saver Preview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 2px solid black;")
        self.preview_label.setFixedHeight(250)
        self.preview_label.mousePressEvent = self.preview_click

        self.speaker_button = QPushButton("🔇")
        self.speaker_button.setFixedSize(40, 40)
        self.speaker_button.clicked.connect(self.toggle_sound)

        preview_layout = QHBoxLayout()
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.addWidget(self.preview_label)

        button_container = QWidget(self.preview_label)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.addWidget(self.speaker_button, alignment=Qt.AlignTop | Qt.AlignRight)
        button_container.setLayout(button_layout)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Screen saver name")
        self.name_input.textChanged.connect(self.check_input_validity)

        self.version_input = QLineEdit()
        self.version_input.setPlaceholderText("Version (e.g., 1.0)")
        self.version_input.setValidator(QRegExpValidator(QRegExp(r"^\d+(\.\d+)*$")))
        self.version_input.textChanged.connect(self.check_input_validity)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Description (max 160 characters)")
        self.desc_input.setFixedHeight(50)
        self.desc_input.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.desc_input.setLineWrapMode(QTextEdit.WidgetWidth)
        self.desc_input.textChanged.connect(self.check_input_validity)

        self.build_button = QPushButton("Build SCR")
        self.build_button.setEnabled(False)
        self.build_button.clicked.connect(self.build_scr)

        self.icon_preview_label = QLabel("Icon")
        self.icon_preview_label.setAlignment(Qt.AlignCenter)
        self.icon_preview_label.setStyleSheet("border: 2px solid black;")
        self.icon_preview_label.mousePressEvent = self.upload_icon

        # Set standard sizes for the icon preview label and build button
        self.icon_preview_label.setFixedSize(60, 60)  # Standard icon preview size
        self.build_button.setFixedSize(60, 30)  # Standard build button size

        name_version_layout = QHBoxLayout()
        name_version_layout.addWidget(self.name_input)
        name_version_layout.addWidget(self.version_input)

        file_controls = QVBoxLayout()
        file_controls.addLayout(name_version_layout)
        file_controls.addWidget(self.desc_input)

        icon_build_layout = QVBoxLayout()
        icon_build_layout.addWidget(self.icon_preview_label)
        icon_build_layout.addWidget(self.build_button)

        controls_layout = QHBoxLayout()
        controls_layout.addLayout(file_controls)
        controls_layout.addLayout(icon_build_layout)

        layout.addLayout(preview_layout)
        layout.addLayout(controls_layout)
        self.setLayout(layout)

    def preview_click(self, event):
        self.upload_gif()

    def upload_gif(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select GIF File", "", "GIF Files (*.gif)")
        if file_name:
            self.gif_path = file_name
            movie = QMovie(file_name)
            self.preview_label.setMovie(movie)
            movie.start()
            self.check_input_validity()

    def toggle_sound(self):
        if not self.sound_enabled:
            self.upload_sound()
        else:
            self.sound_enabled = False
            self.sound_path = None
            self.speaker_button.setText("🔇")

    def upload_sound(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Sound File", "", "Audio Files (*.mp3 *.wav)")
        if file_name:
            self.sound_path = file_name
            self.sound_enabled = True
            self.speaker_button.setText("🔊")

    def upload_icon(self, event):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Icon File", "", "Icon Files (*.ico *.png)")
        if file_name:
            self.icon_path = file_name
            pixmap = QPixmap(file_name).scaled(32, 32)
            self.setWindowIcon(QIcon(pixmap))
            self.icon_preview_label.setPixmap(pixmap)

    def check_input_validity(self):
        name_valid = bool(self.name_input.text().strip())
        version_valid = bool(self.version_input.text().strip()) and self.version_input.hasAcceptableInput()
        description_valid = bool(self.desc_input.toPlainText().strip()) and len(self.desc_input.toPlainText()) <= 160
        gif_valid = self.gif_path is not None
        self.build_button.setEnabled(name_valid and version_valid and description_valid and gif_valid)

    def build_scr(self):
        if not self.gif_path:
            self.show_error_popup("Please upload a GIF file.")
            return

        name = self.name_input.text()
        version = self.version_input.text()
        description = self.desc_input.toPlainText()

        if len(description) > 160:
            self.show_error_popup("Description cannot exceed 160 characters.")
            return

        self.circular_progress = CircularProgress(self)
        center = self.mapToGlobal(self.rect().center()) - QPoint(self.circular_progress.width() // 2, self.circular_progress.height() // 2)
        self.circular_progress.move(center)
        self.circular_progress.show()

        self.progress_value = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(30)

    def update_progress(self):
        if self.progress_value >= 100:
            self.timer.stop()
            QTimer.singleShot(1000, self.circular_progress.close)
        else:
            self.progress_value += 1
            self.circular_progress.setProgress(self.progress_value)

    def show_error_popup(self, message):
        error_label = QLabel(message, self)
        error_label.setStyleSheet("""QLabel {
            background-color: #e53935;
            color: white;
            padding: 10px 20px;
            border-radius: 10px;
            font-size: 14px;
        }""")
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setWindowFlags(Qt.ToolTip)
        error_label.adjustSize()
        center = self.mapToGlobal(self.rect().center()) - QPoint(error_label.width() // 2, error_label.height() // 2)
        error_label.move(center)
        error_label.show()
        QTimer.singleShot(2000, error_label.close)

if __name__ == "__main__":
    app = QApplication([])
    window = GifToScrBuilder()
    window.show()
    app.exec_()
