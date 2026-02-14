from dataclasses import dataclass

from models.episode import Episode


@dataclass
class EpisodeConfig:
    index: int
    episodes: list[Episode]

    def currentEpisode(self) -> Episode:
        return self.episodes[self.index]

    @classmethod
    def fromDict(cls, data: dict) -> "EpisodeConfig":
        return cls(data["index"], [Episode.fromDict(e) for e in data["episodes"]])
