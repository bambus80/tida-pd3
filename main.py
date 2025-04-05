from src.layout import *
from src.player import *
from PyQt5.QtWidgets import QMessageBox
import sys

MUSIC_FOLDER_PATH = "music"

if __name__ == "__main__":
    app = QApplication(sys.argv)
    print(f"Music folder: {os.path.join(os.getcwd(), MUSIC_FOLDER_PATH)}")
    if not os.listdir(MUSIC_FOLDER_PATH):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(f"No files found at {os.path.join(os.getcwd(), MUSIC_FOLDER_PATH)}\nPlease make sure to include music in this directory.")
        sys.exit(msg.exec_())

    playlist_ctl = PlaylistController(MUSIC_FOLDER_PATH)
    music_app = MusicApp(playlist_ctl)
    sys.exit(app.exec_())
