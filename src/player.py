import pygame
import audio_metadata
import os
import random


class PlaylistController:
    def __init__(self, filepath: str) -> None:
        self.idx: int = 0
        self.path: str = filepath
        self.song_list: list[str] = os.listdir(self.path)
        print(f"Total songs: {len(self.song_list)} | {self.song_list}")

        self.metadata: audio_metadata.Format | None = None
        self.is_playing: bool = False
        self.mode: str | None = None

        pygame.mixer.init()
        self._open(self.idx)

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
            pygame.mixer.music.play()
        else:
            print("Resuming song")
            pygame.mixer.music.unpause()
        self.is_playing = True

    def pause(self) -> None:
        print("Pausing song")
        pygame.mixer.music.pause()
        self.is_playing = False

    def stop(self) -> None:
        if not pygame.mixer.music.get_busy():
            print("No song playing, nothing to stop")
        else:
            print("Stopping song")
            pygame.mixer.music.stop()
        self.idx = 0

    def next(self) -> None:
        print("Next song")
        pygame.mixer.music.stop()
        match self.mode:
            case "repeat":
                self.idx = 0 if self.idx == len(self.song_list) - 1 else self.idx + 1
            case "shuffle":
                self.idx = random.randrange(0, len(self.song_list))
            case _:
                if self.idx == len(self.song_list) - 1:
                    self.stop()
                    return
                self.idx += 1
        self._open(self.idx)
        self.play()

    def back(self) -> None:
        print("Previous song")
        pygame.mixer.music.stop()
        if self.idx == 0:
            self.idx = len(self.song_list)
        self.idx -= 1
        self._open(self.idx)
        self.play()

    def get_stream_info(self) -> dict:
        stream_info = self.metadata.streaminfo
        return {
            "title": self.song_list[self.idx],
            "bitrate": stream_info.get("bitrate", "--"),
            "rate": stream_info.get("sample_rate", "--"),
            "channels": stream_info.get("channels", "--")
        }

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
