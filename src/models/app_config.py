from dataclasses import dataclass


@dataclass
class AppConfig:
    folderFile: str
    playlistFile: str
    statusFile: str
    extensions: list[str]
