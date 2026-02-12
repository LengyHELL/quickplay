import simplejson as json

from models.episode import Episode, EpisodeConfig


class PlaylistService:
    def load(self, path: str) -> EpisodeConfig:
        with open(path, "r", encoding="utf-8") as file:
            data = json.loads(file.read())
            episodes = [Episode(**e) for e in data["episodes"]]
            return EpisodeConfig(data["index"], episodes)

    def save(self, path: str, config: EpisodeConfig) -> None:
        with open(path, "w", encoding="utf-8") as file:
            data = {"index": config.index, "episodes": [e.__dict__ for e in config.episodes]}
            file.write(json.dumps(data, indent=2))
