import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QFileDialog, QVBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt

class GifToScrBuilder(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GIF to .SCR Builder")
        self.setFixedSize(400, 380)

        layout = QVBoxLayout()

        # Screensaver Name
        layout.addWidget(QLabel("Screen Saver Name:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        # GIF input
        layout.addWidget(QLabel("GIF File:"))
        self.gif_input = QLineEdit()
        self.gif_input.setReadOnly(True)
        gif_button = QPushButton("Browse GIF")
        gif_button.clicked.connect(self.browse_gif)
        layout.addWidget(self.gif_input)
        layout.addWidget(gif_button)

        # WAV input
        layout.addWidget(QLabel("Sound (.wav) File:"))
        self.wav_input = QLineEdit()
        self.wav_input.setReadOnly(True)
        wav_button = QPushButton("Browse WAV")
        wav_button.clicked.connect(self.browse_wav)
        layout.addWidget(self.wav_input)
        layout.addWidget(wav_button)

        # ICON input
        layout.addWidget(QLabel("Icon (.ico) File:"))
        self.icon_input = QLineEdit()
        self.icon_input.setReadOnly(True)
        icon_button = QPushButton("Browse Icon")
        icon_button.clicked.connect(self.browse_icon)
        layout.addWidget(self.icon_input)
        layout.addWidget(icon_button)

        # Build button
        build_button = QPushButton("Build .SCR")
        build_button.clicked.connect(self.build_scr)
        layout.addWidget(build_button)

        self.setLayout(layout)

    def browse_gif(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select GIF", "", "GIF Files (*.gif)")
        if file_name:
            self.gif_input.setText(file_name)

    def browse_wav(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select WAV", "", "WAV Files (*.wav)")
        if file_name:
            self.wav_input.setText(file_name)

    def browse_icon(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Icon", "", "Icon Files (*.ico)")
        if file_name:
            self.icon_input.setText(file_name)

    def build_scr(self):
        name = self.name_input.text().strip()
        gif_path = self.gif_input.text().strip()
        wav_path = self.wav_input.text().strip()
        icon_path = self.icon_input.text().strip()

        if not name or not gif_path or not wav_path or not icon_path:
            QMessageBox.warning(self, "Missing Info", "All fields are required (including icon).")
            return

        # Write the screensaver player script
        player_code = f"""
import sys
import threading
import pygame
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt

GIF_PATH = r\"\"\"{gif_path}\"\"\"
WAV_PATH = r\"\"\"{wav_path}\"\"\"

class FullscreenFillGifSaver(QLabel):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setGeometry(QApplication.primaryScreen().geometry())
        self.setStyleSheet("background-color: black;")
        self.setAlignment(Qt.AlignCenter)

        self.movie = QMovie(GIF_PATH)
        self.movie.setScaledSize(QApplication.primaryScreen().size())
        self.setMovie(self.movie)
        self.movie.start()

        threading.Thread(target=self.play_sound, daemon=True).start()

    def play_sound(self):
        pygame.mixer.init()
        pygame.mixer.music.load(WAV_PATH)
        pygame.mixer.music.play(-1)

    def keyPressEvent(self, event): QApplication.quit()
    def mouseMoveEvent(self, event): QApplication.quit()
    def mousePressEvent(self, event): QApplication.quit()
    def wheelEvent(self, event): QApplication.quit()
    def touchEvent(self, event): QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    saver = FullscreenFillGifSaver()
    saver.show()
    sys.exit(app.exec_())
"""

        script_path = "temp_screensaver.py"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(player_code)

        # Build with PyInstaller and icon
        base_name = name.replace(" ", "_")
        exe_name = base_name + ".exe"
        scr_name = base_name + ".scr"
        build_cmd = f'pyinstaller --noconfirm --onefile --windowed --icon="{icon_path}" --name="{exe_name}" "{script_path}"'
        subprocess.run(build_cmd, shell=True)

        # Move to Desktop and rename
        dist_path = os.path.join("dist", exe_name)
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", scr_name)

        if os.path.exists(dist_path):
            os.replace(dist_path, desktop_path)
            QMessageBox.information(self, "Success", f"{scr_name} saved to Desktop!")
        else:
            QMessageBox.critical(self, "Build Failed", "Could not build .scr file.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GifToScrBuilder()
    window.show()
    sys.exit(app.exec_())
