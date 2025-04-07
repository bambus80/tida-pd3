from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from src.player import *


class MusicApp(QWidget):
    def __init__(self, playlist_ctl: PlaylistController) -> None:
        super().__init__()
        self.setGeometry(100, 100, 550, 200)
        self.playlist_ctl: PlaylistController = playlist_ctl
        self.setLayout(self.main_layout())
        self.show()

    def main_layout(self) -> QLayout:
        layout = QGridLayout()
        layout.addWidget(self.top_left_display(), 0, 0)
        layout.addLayout(self.transport_buttons(), 1, 0)
        layout.addLayout(self.song_info(), 0, 1)
        layout.addLayout(self.left_buttons(), 1, 1)
        return layout

    def top_left_display(self) -> QLabel:
        label = QLabel()
        # label.setStyleSheet("border: 1px solid #ccc")
        pixmap = QPixmap("src/assets/blank.png")  # TODO: Display album cover
        pixmap = pixmap.scaledToWidth(128)
        pixmap = pixmap.scaledToHeight(128)
        label.setPixmap(pixmap)
        return label

    def transport_buttons(self) -> QLayout:
        def do(x): return lambda: (x(), self.update_song_info())  # Update on-screen info after performing X

        # TODO: Implement nice icons for transport buttons
        layout = QHBoxLayout()
        go_back_button = QPushButton(self)
        go_back_button.setText("<-")
        go_back_button.clicked.connect(do(self.playlist_ctl.back))
        layout.addWidget(go_back_button)
        play_button = QPushButton(self)
        play_button.setText(">")
        play_button.clicked.connect(do(self.playlist_ctl.play))
        layout.addWidget(play_button)
        pause_button = QPushButton(self)
        pause_button.setText("||")
        pause_button.clicked.connect(do(self.playlist_ctl.pause))
        layout.addWidget(pause_button)
        stop_button = QPushButton(self)
        stop_button.setText("[]")
        stop_button.clicked.connect(do(self.playlist_ctl.stop))
        layout.addWidget(stop_button)
        go_forward_button = QPushButton(self)
        go_forward_button.setText("->")
        go_forward_button.clicked.connect(do(self.playlist_ctl.next))
        layout.addWidget(go_forward_button)
        return layout

    def song_info(self) -> QLayout:
        layout = QGridLayout()
        self.song_title_label = QLabel("<b>Song title</b>")
        self.song_title_label.setStyleSheet("font: 16pt")
        layout.addWidget(self.song_title_label, 0, 0)
        self.bitrate_label = QLabel("<b>Bitrate:</b> --")
        layout.addWidget(self.bitrate_label, 1, 0)
        self.sampling_rate_label = QLabel("<b>Sampling rate:</b> --")
        layout.addWidget(self.sampling_rate_label, 1, 1)
        self.channel_label = QLabel("<b>-- Channels</b>")
        layout.addWidget(self.channel_label, 2, 0)

        # TODO: Implement volume slider
        volume_slider_layout = QHBoxLayout()
        volume_slider_layout.addWidget(QLabel("<b>Volume:</b>"))
        volume_slider = QSlider()
        volume_slider.setOrientation(1)  # 1 means horizontal
        volume_slider.setValue(1)        # 100%
        volume_slider.valueChanged.connect(self.playlist_ctl.set_volume)
        volume_slider_layout.addWidget(volume_slider)
        layout.addLayout(volume_slider_layout, 2, 1)

        self.playlist_status_label = QLabel("""
            <font color=\"black\"><b>Shuffle</b></font>
            <font color=\"black\"><b>Repeat</b></font>
        """)
        self.playlist_status_label.setStyleSheet("border: 1px solid #ccc")
        layout.addWidget(self.playlist_status_label, 3, 0)
        return layout

    def update_song_info(self) -> None:
        metadata = self.playlist_ctl.get_stream_info()
        self.song_title_label.setText(f"<b>{metadata['title']}</b>")
        self.bitrate_label.setText(f"<b>Bitrate:</b> {metadata['bitrate']}")
        self.sampling_rate_label.setText(f"<b>Sampling rate:</b> {metadata['rate']}")
        self.channel_label.setText(f"<b>{metadata['channels']} Channels</b>")
        self.playlist_status_label.setText(f"""
                    <font color=\"{"red" if self.playlist_ctl.mode == "shuffle" else "black"}\"><b>Shuffle</b></font>
                    <font color=\"{"red" if self.playlist_ctl.mode == "repeat" else "black"}\"><b>Repeat</b></font>
                """)

    def left_buttons(self) -> QLayout:
        def do(x): return lambda: (x(), self.update_song_info())  # Update on-screen info after performing X

        layout = QHBoxLayout()
        shuffle_button = QPushButton(self)
        shuffle_button.setText("Shuffle")
        shuffle_button.clicked.connect(do(self.playlist_ctl.toggle_shuffle))
        layout.addWidget(shuffle_button)
        repeat_button = QPushButton(self)
        repeat_button.setText("Repeat")
        repeat_button.clicked.connect(do(self.playlist_ctl.toggle_repeat))
        layout.addWidget(repeat_button)
        return layout
