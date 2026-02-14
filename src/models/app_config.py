from dataclasses import dataclass


@dataclass
class AppConfig:
    playlistConfig: str
    folders: list[str]
    extensions: list[str]

    @classmethod
    def fromDict(cls, data: dict) -> "AppConfig":
        return cls(**data)
