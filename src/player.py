from audioplayer import AudioPlayer
import audio_metadata
import os
import random


class PlaylistController:
    def __init__(self, filepath: str) -> None:
        self.idx: int = 0
        self.path: str = filepath
        self.song_list: list[str] = os.listdir(self.path)
        print(f"Total songs: {len(self.song_list)} | {self.song_list}")

        self.player: AudioPlayer | None = None
        self.metadata: audio_metadata.Format | None = None
        self.is_playing: bool = False
        self.mode: str | None = None
        self._open(self.idx)

    def _open(self, idx: int) -> None:
        print(f"Opening {self.song_list[idx]}... ", end="")
        path = f"{self.path}/{self.song_list[idx]}"
        try:
            if self.is_playing:
                self.is_playing = False
                self.player.close()
            self.metadata = audio_metadata.load(path)
            self.player = AudioPlayer(path)
        except Exception as e:
            print(f"FAILED! {e}")
        print("OK")

    def play(self) -> None:
        if not self.is_playing:
            print("Resuming currnet song")
            self.player.resume()
        else:
            print("Playing song")
            self.player.play()
        self.is_playing = True

    def pause(self) -> None:
        print("Pausing song")
        self.player.pause()
        self.is_playing = False

    def stop(self) -> None:
        if not self.player:
            print("Player already closed, no need to stop")
        print("Stopping song")
        self.player.stop()
        self.idx = 0
        # self._open(0)

    def next(self) -> None:
        self.player.close()
        match self.mode:
            case "repeat":
                if self.idx == len(self.song_list) - 1:
                    self.idx = 0
                else:
                    self.idx += 1
            case "shuffle":
                self.idx = random.randrange(0, len(self.song_list))
            case _:
                if self.idx == len(self.song_list) - 1:
                    self.stop()
                self.idx += 1
        self._open(self.idx)

    def get_stream_info(self) -> dict:
        stream_info = self.metadata.streaminfo
        return {
            "title": self.song_list[self.idx],
            "bitrate": stream_info.get("bitrate", "--"),
            "rate": stream_info.get("sample_rate", "--"),
            "channels": stream_info.get("channels", "--")
        }
