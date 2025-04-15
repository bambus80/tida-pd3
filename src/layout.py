from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from src.player import *
from src.util import *


class MusicApp(QWidget):
    def __init__(self, playlist_ctl: PlaylistController) -> None:
        super().__init__()
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_seek_position)
        self.timer.start()

        self.setWindowTitle("Super cool music player")
        self.setGeometry(100, 100, 550, 200)
        self.old_idx = 0
        self.playlist_ctl: PlaylistController = playlist_ctl
        self.playlist_ctl.song_updated.connect(self.update_song_info)

        self.user_dragging_slider: bool = False
        self.setLayout(self.main_layout())
        self.show()

    def main_layout(self) -> QLayout:
        layout = QVBoxLayout()
        grid = QGridLayout()
        self.duration_label = QLabel("<b>Stopped</b> --:--/--:--")
        self.duration_label.setStyleSheet("font: 12pt")
        self.song_title_label = QLabel("<b>Press Play button to start</b>")
        self.song_title_label.setStyleSheet("font: 12pt")
        grid.addWidget(self.duration_label, 0, 0)
        grid.addWidget(self.song_title_label, 0, 1)
        grid.addWidget(self.top_left_display(), 1, 0)
        grid.addLayout(self.transport_buttons(), 2, 0)
        grid.addLayout(self.song_info(), 1, 1)
        grid.addLayout(self.left_buttons(), 2, 1)
        layout.addLayout(grid)
        layout.addLayout(self.song_duration_bar())
        return layout

    def top_left_display(self) -> QLabel:
        self.album_label = QLabel()
        self.album_pixmap = QPixmap("src/assets/blank.png")
        self.album_pixmap = self.album_pixmap.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.album_label.setPixmap(self.album_pixmap)
        return self.album_label

    def transport_buttons(self) -> QLayout:
        def do(x): return lambda: (x(), self.update_song_info())  # Update on-screen info after performing X

        layout = QHBoxLayout()
        go_back_button = QPushButton(self)
        go_back_button.setIcon(QIcon("src/assets/icon_back.png"))
        go_back_button.clicked.connect(do(self.playlist_ctl.back))
        layout.addWidget(go_back_button)
        play_button = QPushButton(self)
        play_button.setIcon(QIcon("src/assets/icon_play.png"))
        play_button.clicked.connect(do(self.playlist_ctl.play))
        layout.addWidget(play_button)
        pause_button = QPushButton(self)
        pause_button.setIcon(QIcon("src/assets/icon_pause.png"))
        pause_button.clicked.connect(do(self.playlist_ctl.pause))
        layout.addWidget(pause_button)
        stop_button = QPushButton(self)
        stop_button.setIcon(QIcon("src/assets/icon_stop.png"))
        stop_button.clicked.connect(lambda: (self.playlist_ctl.stop(), self.reset_song_info()))
        layout.addWidget(stop_button)
        go_forward_button = QPushButton(self)
        go_forward_button.setIcon(QIcon("src/assets/icon_next.png"))
        go_forward_button.clicked.connect(do(self.playlist_ctl.force_next))
        layout.addWidget(go_forward_button)
        return layout

    def song_info(self) -> QLayout:
        layout = QVBoxLayout()
        grid = QGridLayout()
        # layout.addWidget(self.song_title_label)
        self.bitrate_label = QLabel("<b>Bitrate:</b> --")
        grid.addWidget(self.bitrate_label, 1, 0)
        self.sampling_rate_label = QLabel("<b>Mixrate:</b> --")
        grid.addWidget(self.sampling_rate_label, 1, 1)
        self.channel_label = QLabel("<b>-- Channels</b>")
        grid.addWidget(self.channel_label, 1, 2)

        volume_slider_layout = QHBoxLayout()
        volume_slider_layout.addWidget(QLabel("<b>Volume:</b>"))
        volume_slider = QSlider()
        volume_slider.setOrientation(1)  # 1 means horizontal
        volume_slider.setRange(0, 100)
        volume_slider.setValue(100)
        volume_slider.valueChanged.connect(lambda val: self.playlist_ctl.set_volume(val / 100))
        volume_slider_layout.addWidget(volume_slider)

        self.playlist_status_label = QLabel("""
            <font color=\"black\"><b>Shuffle</b></font>
            <font color=\"black\"><b>Repeat</b></font>
        """)
        self.playlist_status_label.setStyleSheet("border: 1px solid #ccc")
        layout.addLayout(grid)
        layout.addLayout(volume_slider_layout)
        layout.addWidget(self.playlist_status_label)
        return layout

    def new_album_cover(self, cover: QPixmap = None) -> None:
        if cover:
            self.album_pixmap = cover
        else:
            self.album_pixmap = QPixmap("src/assets/blank.png")
        self.album_pixmap = self.album_pixmap.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.album_label.setPixmap(self.album_pixmap)

    def update_song_info(self) -> None:
        if self.playlist_ctl.state in ["playing", "paused", "opened"]:
            metadata = self.playlist_ctl.get_stream_info()
            self.song_title_label.setText(f"<b>{truncate(metadata['title'], 40)}</b>")
            self.bitrate_label.setText(f"<b>Bitrate:</b> {str(metadata['bitrate'] / 1000) + 'kbps'}")
            self.sampling_rate_label.setText(f"<b>Mixrate:</b> {str(metadata['rate'] / 1000) + 'kHz'}")
            self.duration_label.setText(
                f"""
                <b>{self.playlist_ctl.state.capitalize()}</b> 
                {secs_to_mmss(metadata['offset'] * 2)}/{secs_to_mmss(metadata['duration'])}
                """)  # ???
            self.channel_label.setText(f"<b>{metadata['channels']} channel(s)</b>")
        if not self.old_idx == self.playlist_ctl.idx:
            self.new_album_cover(self.playlist_ctl.get_album_cover())
        self.playlist_status_label.setText(f"""
                    <font color=\"{"red" if self.playlist_ctl.mode == "shuffle" else "black"}\"><b>Shuffle</b></font>
                    <font color=\"{"red" if self.playlist_ctl.mode == "repeat" else "black"}\"><b>Repeat</b></font>
                """)
        self.old_idx = self.playlist_ctl.idx

    def reset_song_info(self) -> None:
        self.song_duration_slider.setValue(0)
        self.song_title_label.setText("<b>Press Play button to start</b>")
        self.bitrate_label.setText("<b>Bitrate:</b> --")
        self.sampling_rate_label.setText("<b>Mixrate:</b> --")
        self.duration_label.setText("<b>Stopped</b> --:--/--:--")
        self.channel_label.setText("<b>-- channel(s)</b>")
        self.new_album_cover()
        self.playlist_status_label.setText(f"""
                    <font color=\"{"red" if self.playlist_ctl.mode == "shuffle" else "black"}\"><b>Shuffle</b></font>
                    <font color=\"{"red" if self.playlist_ctl.mode == "repeat" else "black"}\"><b>Repeat</b></font>
                """)

    def left_buttons(self) -> QLayout:
        def do(x): return lambda: (x(), self.update_song_info())  # Update on-screen info after performing X

        layout = QHBoxLayout()
        self.shuffle_button = QPushButton(self)
        self.shuffle_button.setIcon(QIcon("src/assets/icon_shuffle.png"))
        self.shuffle_button.clicked.connect(do(self.playlist_ctl.toggle_shuffle))
        layout.addWidget(self.shuffle_button)
        self.repeat_button = QPushButton(self)
        self.repeat_button.setIcon(QIcon("src/assets/icon_repeat.png"))
        self.repeat_button.clicked.connect(do(self.playlist_ctl.toggle_repeat))
        layout.addWidget(self.repeat_button)
        return layout

    def song_duration_bar(self) -> QLayout:
        layout = QHBoxLayout()
        self.song_duration_slider = QSlider()
        self.song_duration_slider.setOrientation(1)  # 1 means horizontal
        self.song_duration_slider.setRange(0, 1000)
        layout.addWidget(self.song_duration_slider)
        return layout

    def update_seek_position(self) -> None:
        self.playlist_ctl.update()
        if self.user_dragging_slider:
            return
        if self.playlist_ctl.state == "playing" and self.playlist_ctl.get_current_pos() is not None:
            pos = self.playlist_ctl.get_current_pos()
            duration = self.playlist_ctl.get_stream_info()['duration']
            if duration:
                percent = int((pos / duration) * 1000)
                self.song_duration_slider.setValue(percent)
        elif not self.playlist_ctl.state == "paused":
            self.song_duration_slider.setValue(0)
