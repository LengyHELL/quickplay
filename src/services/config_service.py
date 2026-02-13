import os

import simplejson as json

from models.app_config import AppConfig
from models.episode import Episode, EpisodeConfig

APP_CONFIG_PATH = "_internal/config.json"


class ConfigService:
    def loadAppConfig(self) -> AppConfig:
        if os.path.isfile(APP_CONFIG_PATH):
            with open(APP_CONFIG_PATH, "r", encoding="utf-8") as file:
                data = json.loads(file.read())
                return AppConfig(**data)
        else:
            config = AppConfig("_internal/quickplay.json", "quickplay.json", ["C:\\Users\\Public"], [".mkv", ".mp4"])
            self.saveAppConfig(config)
            return config

    def saveAppConfig(self, config: AppConfig) -> None:
        with open(APP_CONFIG_PATH, "w", encoding="utf-8") as file:
            data = config.__dict__
            file.write(json.dumps(data, indent=2))

    def loadEpisodeConfig(self, path: str) -> EpisodeConfig:
        with open(path, "r", encoding="utf-8") as file:
            data = json.loads(file.read())
            episodes = [Episode(**e) for e in data["episodes"]]
            return EpisodeConfig(data["index"], episodes)

    def saveEpisodeConfig(self, path: str, config: EpisodeConfig) -> None:
        with open(path, "w", encoding="utf-8") as file:
            data = {"index": config.index, "episodes": [e.__dict__ for e in config.episodes]}
            file.write(json.dumps(data, indent=2))
