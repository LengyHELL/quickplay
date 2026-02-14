import os
from dataclasses import asdict

import simplejson as json

from models.app_config import AppConfig
from models.playlist_config import PlaylistConfig

APP_CONFIG_PATH = "_internal/config.json"


class ConfigService:
    def _createDefaultConfig(self) -> AppConfig:
        return AppConfig.fromDict(
            {
                "playlistConfig": "_internal/quickplay.json",
                "folders": ["C:\\Users\\Public"],
                "extensions": [".mkv", ".mp4"],
            }
        )

    def _createDefaultPlaylistConfig(self) -> PlaylistConfig:
        return PlaylistConfig.fromDict({"previous": {"index": 0, "episodes": []}, "titles": []})

    def loadAppConfig(self) -> AppConfig:
        if os.path.isfile(APP_CONFIG_PATH):
            with open(APP_CONFIG_PATH, "r", encoding="utf-8") as file:
                return AppConfig.fromDict(json.loads(file.read()))
        else:
            config = self._createDefaultConfig()
            self.saveAppConfig(config)
            return config

    def saveAppConfig(self, config: AppConfig) -> None:
        with open(APP_CONFIG_PATH, "w", encoding="utf-8") as file:
            file.write(json.dumps(asdict(config), indent=2))

    def loadPlaylistConfig(self, path: str) -> PlaylistConfig:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as file:
                return PlaylistConfig.fromDict(json.loads(file.read()))
        else:
            config = self._createDefaultPlaylistConfig()
            self.savePlaylistConfig(path, config)
            return config

    def savePlaylistConfig(self, path: str, config: PlaylistConfig) -> None:
        with open(path, "w", encoding="utf-8") as file:
            file.write(json.dumps(asdict(config), indent=2))
