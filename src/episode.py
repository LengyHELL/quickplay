class Episode:
    name: str
    path: str
    progress: float
    completed: bool

    def __init__(self, name: str, path: str, progress: float, completed: bool) -> None:
        self.name = name
        self.path = path
        self.progress = progress
        self.completed = completed


class EpisodeConfig:
    index: int
    episodes: list[Episode]

    def __init__(self, index: int, episodes: list[Episode]) -> None:
        self.index = index
        self.episodes = episodes

    def currentEpisode(self) -> Episode:
        return self.episodes[self.index]
