from src.layout import *
from src.player import *
from PyQt5.QtWidgets import QMessageBox
import sys


if __name__ == "__main__":
    MUSIC_FOLDER_PATH = "music"
    app = QApplication(sys.argv)
    path = os.path.join(os.getcwd(), sys.argv[1] if len(sys.argv) >= 2 else MUSIC_FOLDER_PATH)
    print(f"Music folder: {path}")
    if not os.listdir(path):
        msg = QMessageBox()
        msg.setWindowTitle("Super cool music player")
        msg.setIcon(QMessageBox.Critical)
        msg.setText(f"No files found at {path}\nPlease make sure to include music in this directory.")
        sys.exit(msg.exec_())

    playlist_ctl = PlaylistController(MUSIC_FOLDER_PATH)
    music_app = MusicApp(playlist_ctl)
    sys.exit(app.exec_())
