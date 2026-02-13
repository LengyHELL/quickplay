from dataclasses import dataclass


@dataclass
class AppConfig:
    playlistFile: str
    statusFile: str
    folders: list[str]
    extensions: list[str]
