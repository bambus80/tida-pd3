from PyQt5.QtCore import QTimer
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

        self.setGeometry(100, 100, 550, 200)
        self.playlist_ctl: PlaylistController = playlist_ctl
        self.setLayout(self.main_layout())
        self.show()

    def main_layout(self) -> QLayout:
        layout = QVBoxLayout()
        grid = QGridLayout()
        grid.addWidget(self.top_left_display(), 0, 0)
        grid.addLayout(self.transport_buttons(), 1, 0)
        grid.addLayout(self.song_info(), 0, 1)
        grid.addLayout(self.left_buttons(), 1, 1)
        layout.addLayout(grid)
        layout.addLayout(self.song_duration_bar())
        return layout

    def top_left_display(self) -> QLabel:
        label = QLabel()
        pixmap = QPixmap("src/assets/blank.png")  # TODO: Display album cover
        pixmap = pixmap.scaledToWidth(128)
        pixmap = pixmap.scaledToHeight(128)
        label.setPixmap(pixmap)
        return label

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
        go_forward_button.clicked.connect(do(self.playlist_ctl.next))
        layout.addWidget(go_forward_button)
        return layout

    def song_info(self) -> QLayout:
        layout = QVBoxLayout()
        grid = QGridLayout()
        self.song_title_label = QLabel("<b>Press Play button to start</b>")
        self.song_title_label.setStyleSheet("font: 16pt")
        grid.addWidget(self.song_title_label, 0, 0)
        self.bitrate_label = QLabel("<b>Bitrate:</b> --")
        grid.addWidget(self.bitrate_label, 1, 0)
        self.sampling_rate_label = QLabel("<b>Sampling rate:</b> --")
        grid.addWidget(self.sampling_rate_label, 1, 1)
        self.duration_label = QLabel("<b>Stopped</b> --:--/--:--")
        grid.addWidget(self.duration_label, 2, 0)
        self.channel_label = QLabel("<b>-- Channels</b>")
        grid.addWidget(self.channel_label, 2, 1)

        # TODO: Implement volume slider
        volume_slider_layout = QHBoxLayout()
        volume_slider_layout.addWidget(QLabel("<b>Volume:</b>"))
        volume_slider = QSlider()
        volume_slider.setOrientation(1)  # 1 means horizontal
        volume_slider.setRange(0, 100)
        volume_slider.setValue(100)
        volume_slider.valueChanged.connect(lambda val: self.playlist_ctl.set_volume(val / 100))
        volume_slider_layout.addWidget(volume_slider)
        layout.addLayout(volume_slider_layout)

        self.playlist_status_label = QLabel("""
            <font color=\"black\"><b>Shuffle</b></font>
            <font color=\"black\"><b>Repeat</b></font>
        """)
        self.playlist_status_label.setStyleSheet("border: 1px solid #ccc")
        layout.addLayout(grid)
        layout.addLayout(volume_slider_layout)
        layout.addWidget(self.playlist_status_label)
        return layout

    def update_song_info(self) -> None:
        if self.playlist_ctl.is_playing:
            metadata = self.playlist_ctl.get_stream_info()
            self.song_title_label.setText(f"<b>{metadata['title']}</b>")
            self.bitrate_label.setText(f"<b>Bitrate:</b> {str(metadata['bitrate'] / 1000) + 'kbps'}")
            self.sampling_rate_label.setText(f"<b>Sampling rate:</b> {str(metadata['rate'] / 1000) + 'kHz'}")
            self.duration_label.setText(
                f"<b>{'Playing' if self.playlist_ctl.is_playing else 'Paused'}</b> --:--/{secs_to_mmss(metadata['duration'])}")
            self.channel_label.setText(f"<b>{metadata['channels']} Channels</b>")
        self.playlist_status_label.setText(f"""
                    <font color=\"{"red" if self.playlist_ctl.mode == "shuffle" else "black"}\"><b>Shuffle</b></font>
                    <font color=\"{"red" if self.playlist_ctl.mode == "repeat" else "black"}\"><b>Repeat</b></font>
                """)

    def reset_song_info(self) -> None:
        self.song_title_label.setText("<b>Press Play button to start</b>")
        self.bitrate_label.setText("<b>Bitrate:</b> --")
        self.sampling_rate_label.setText("<b>Sampling rate:</b> --")
        self.duration_label.setText("<b>Stopped</b> --:--/--:--")
        self.channel_label.setText("<b>-- Channels</b>")
        self.playlist_status_label.setText(f"""
                            <font color=\"{"red" if self.playlist_ctl.mode == "shuffle" else "black"}\"><b>Shuffle</b></font>
                            <font color=\"{"red" if self.playlist_ctl.mode == "repeat" else "black"}\"><b>Repeat</b></font>
                        """)

    def left_buttons(self) -> QLayout:
        def do(x): return lambda: (x(), self.update_song_info())  # Update on-screen info after performing X

        layout = QHBoxLayout()
        shuffle_button = QPushButton(self)
        shuffle_button.setIcon(QIcon("src/assets/icon_shuffle.png"))
        shuffle_button.clicked.connect(do(self.playlist_ctl.toggle_shuffle))
        layout.addWidget(shuffle_button)
        repeat_button = QPushButton(self)
        repeat_button.setIcon(QIcon("src/assets/icon_repeat.png"))
        repeat_button.clicked.connect(do(self.playlist_ctl.toggle_repeat))
        layout.addWidget(repeat_button)
        return layout

    def song_duration_bar(self) -> QLayout:
        layout = QHBoxLayout()
        self.song_duration_slider = QSlider()
        self.song_duration_slider.setOrientation(1)  # 1 means horizontal
        self.song_duration_slider.setRange(0, 100)
        self.song_duration_slider.sliderReleased.connect(self._song_seek)
        layout.addWidget(self.song_duration_slider)
        return layout

    def update_seek_position(self):
        if self.playlist_ctl.is_playing and self.playlist_ctl.get_current_pos() is not None:
            pos = self.playlist_ctl.get_current_pos()
            duration = self.playlist_ctl.get_stream_info()['duration']
            if duration:
                percent = int((pos / duration) * 100)
                self.song_duration_slider.setValue(percent)

    def _song_seek(self):
        duration = self.playlist_ctl.get_stream_info()['duration']
        target = (self.song_duration_slider.value() / 100) * duration
        self.playlist_ctl.seek(target)
        self.update_song_info()
