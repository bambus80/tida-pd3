import pygame
import audio_metadata
import os
import random
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QByteArray, QBuffer, QIODevice


class PlaylistController:
    def __init__(self, filepath: str) -> None:
        self.idx: int = 0
        self.path: str = filepath
        self.song_list: list[str] = os.listdir(self.path)
        print(f"Total songs: {len(self.song_list)} | {self.song_list}")

        self.metadata: audio_metadata.Format | None = None
        self.offset: float = 0.0
        self.is_playing: bool = False
        self.mode: str | None = None

        pygame.mixer.init()
        self._open(self.idx)

        self.SONG_END = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.SONG_END)

    def _open(self, idx: int) -> None:
        path = os.path.join(os.getcwd(), self.path, self.song_list[idx])
        print(f"Opening {path}... ", end="")
        try:
            if self.is_playing:
                pygame.mixer.music.stop()
            self.metadata = audio_metadata.load(path)
            pygame.mixer.music.load(path)
        except Exception as e:
            print(f"FAILED! {e}")
            return
        print("OK")

    def play(self) -> None:
        if not self.is_playing:
            print("Playing song")
            self._open(self.idx)
            pygame.mixer.music.play()
            self.offset = 0.0
        else:
            print("Resuming song")
            pygame.mixer.music.unpause()
        self.is_playing = True

    def pause(self) -> None:
        print("Pausing song")
        pygame.mixer.music.pause()

    def stop(self) -> None:
        if not pygame.mixer.music.get_busy():
            print("No song playing, nothing to stop")
        else:
            print("Stopping song")
            pygame.mixer.music.stop()
        self.is_playing = False
        self.offset = 0.0
        self.idx = 0

    def next(self) -> None:
        print("Next song")
        self.stop()
        match self.mode:
            case "repeat":
                ...
            case "shuffle":
                self.idx = random.randrange(0, len(self.song_list))
            case _:
                if self.idx == len(self.song_list):
                    self.stop()
                    return
                self.idx += 1
        self._open(self.idx)
        self.play()

    def back(self) -> None:
        print("Previous song")
        pygame.mixer.music.stop()
        self.offset = 0.0
        self.is_playing = False
        if self.idx == 0:
            self.idx = len(self.song_list)
        self.idx -= 1
        self.play()

    def update(self):
        if self.is_playing and not pygame.mixer.music.get_busy():
            self.next()

    def get_stream_info(self) -> dict:
        stream_info = self.metadata.streaminfo
        return {
            "title": self.song_list[self.idx],
            "bitrate": stream_info.get("bitrate", "--"),
            "rate": stream_info.get("sample_rate", "--"),
            "channels": stream_info.get("channels", "--"),
            "duration": stream_info["duration"] if stream_info.get("duration") else 0.0,
            "offset": self.offset
        }

    def get_current_pos(self) -> float | None:
        pos = pygame.mixer.music.get_pos()
        return pos / 1000 + self.offset if pos != -1 else None

    def get_album_cover(self) -> QPixmap | None:
        if not self.metadata.pictures or not self.is_playing:
            return None
        print("Loading album cover")
        picture = self.metadata.pictures[0]
        # Convert Picture object to QPixmap
        byte_array = QByteArray(picture.data)
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.ReadOnly)
        pixmap = QPixmap()
        pixmap.loadFromData(byte_array, picture.mime_type.split("/")[-1].upper())
        return pixmap

    def seek(self, seconds: float) -> None:
        print(f"Seeking to {seconds} sec...")
        self.offset = seconds
        pygame.mixer.music.play(start=seconds)

    def set_volume(self, value: float) -> None:
        pygame.mixer.music.set_volume(value)

    def toggle_shuffle(self) -> None:
        if self.mode == "shuffle":
            self.mode = None
            print("Disabled shuffle")
        else:
            self.mode = "shuffle"
            print("Enabled shuffle")

    def toggle_repeat(self) -> None:
        if self.mode == "repeat":
            self.mode = None
            print("Disabled repeat")
        else:
            self.mode = "repeat"
            print("Enabled repeat")
