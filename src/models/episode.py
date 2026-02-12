from dataclasses import dataclass


@dataclass
class Episode:
    name: str
    path: str
    base: str
    progress: float
    completed: bool


@dataclass
class EpisodeConfig:
    index: int
    episodes: list[Episode]

    def currentEpisode(self) -> Episode:
        return self.episodes[self.index]
