from dataclasses import dataclass

from models.episode_config import EpisodeConfig
from models.title import Title


@dataclass
class TitleConfig:
    title: Title
    episodeConfig: EpisodeConfig

    @classmethod
    def fromDict(cls, data: dict) -> "TitleConfig":
        return cls(Title.fromDict(data["title"]), EpisodeConfig.fromDict(data["episodeConfig"]))
