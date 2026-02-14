from dataclasses import dataclass

from models.episode import Episode
from models.episode_config import EpisodeConfig
from models.title import Title
from models.title_config import TitleConfig


@dataclass
class PlaylistConfig:
    previous: EpisodeConfig
    titles: list[TitleConfig]

    def _updateEpisodes(self, index: int, episodes: list[Episode]) -> list[Episode]:
        storedEpisodes = self.titles[index].episodeConfig.episodes

        for episode in episodes:
            try:
                index = [s.path for s in storedEpisodes].index(episode.path)
                storedEpisode = storedEpisodes[index]
                storedEpisode.progress = max(storedEpisode.progress, episode.progress)
                storedEpisode.completed = storedEpisode.completed or episode.completed
            except ValueError:
                storedEpisodes.append(episode)

    def updatePrevious(self, previous: EpisodeConfig) -> None:
        self.previous = previous

    def updateTitles(self, title: Title, episodeConfig: EpisodeConfig) -> EpisodeConfig:
        try:
            index = [t.title for t in self.titles].index(title)
            storedTitle = self.titles[index]
            storedTitle.episodeConfig.index = max(storedTitle.episodeConfig.index, episodeConfig.index)
            self._updateEpisodes(index, episodeConfig.episodes)
            return storedTitle.episodeConfig
        except ValueError:
            self.titles.append(TitleConfig(title, EpisodeConfig(0, episodeConfig.episodes)))
            return episodeConfig

    @classmethod
    def fromDict(cls, data: dict) -> "PlaylistConfig":
        return cls(
            EpisodeConfig.fromDict(data["previous"]),
            [TitleConfig.fromDict(t) for t in data["titles"]],
        )
