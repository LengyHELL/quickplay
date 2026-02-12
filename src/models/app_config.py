from dataclasses import dataclass


@dataclass
class AppConfig:
    folderFile: str
    playlistFile: str
    extensions: list[str]
