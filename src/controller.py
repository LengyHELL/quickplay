import os

from PyQt6.QtWidgets import QApplication

from models.app_config import AppConfig
from models.episode import Episode, EpisodeConfig
from models.page import Page
from models.title import Title
from services.directory_service import DirectoryService
from services.episode_service import EpisodeService
from services.playlist_service import PlaylistService
from views.main_window import MainWindow


class QuickplayController:
    def __init__(
        self,
        config: AppConfig,
        view: MainWindow,
        directoryService: DirectoryService,
        playlistService: PlaylistService,
        episodeService: EpisodeService,
    ) -> None:
        self._config = config
        self._view = view
        self._directoryService = directoryService
        self._playlistService = playlistService
        self._episodeService = episodeService

        titles = self._directoryService.scanTitles(config.folderFile, config.extensions)
        self._view.titleSelect.setTitles(titles)

        self._connectSignals()

    def _connectSignals(self) -> None:
        self._view.titleSelect.titleSelected.connect(self._onTitleSelected)
        self._view.titleSelect.startPreviousClicked.connect(self._onStartPrevious)
        self._view.episodeSelect.backClicked.connect(self._onBackToTitles)
        self._view.episodeSelect.episodesSelected.connect(self._onEpisodesSelected)
        self._view.playerPage.stopRequested.connect(self._onStopPlayback)
        self._view.playerPage.player.quitEvent.connect(self._onStopPlayback)
        self._view.playerPage.player.isFullscreen.connect(self._onFullscreen)
        QApplication.instance().aboutToQuit.connect(self._saveConfig)

    def _onTitleSelected(self, title: Title) -> None:
        episodes = self._directoryService.scanEpisodes(title, self._config.extensions)

        statusFilePath = os.path.join(title.base, title.name, self._config.statusFile)
        if os.path.isfile(statusFilePath):
            statusEpisodes = self._episodeService.load(statusFilePath)
            episodes = self._episodeService.matchEpisodes(episodes, statusEpisodes)
        self._episodeService.save(statusFilePath, episodes)

        self._view.episodeSelect.setEpisodes(episodes)
        self._view.setPage(Page.EPISODES)

    def _onStartPrevious(self) -> None:
        config = self._playlistService.load(self._config.playlistFile)
        self._startPlayback(config)

    def _onEpisodesSelected(self, episodes: list[Episode]) -> None:
        config = EpisodeConfig(0, episodes)
        self._playlistService.save(self._config.playlistFile, config)
        self._startPlayback(config)

    def _startPlayback(self, config: EpisodeConfig) -> None:
        self._view.playerPage.player.loadEpisodes(config)
        self._view.setPage(Page.PLAYER)
        self._view.playerPage.player.start()

    def _onStopPlayback(self) -> None:
        self._view.playerPage.player.stop()
        self._saveConfig()
        self._onFullscreen(False)
        if self._view.titleSelect.hasSelection():
            self._view.setPage(Page.EPISODES)
        else:
            self._view.setPage(Page.TITLES)

    def _onFullscreen(self, fullscreen: bool) -> None:
        if fullscreen:
            self._view.showFullScreen()
            self._view.playerPage.setControlsVisible(False)
        else:
            self._view.showNormal()
            self._view.playerPage.setControlsVisible(True)

    def _onBackToTitles(self) -> None:
        self._view.setPage(Page.TITLES)

    def _saveConfig(self) -> None:
        try:
            episodeConfig = self._view.playerPage.player.episodeConfig
            self._playlistService.save(self._config.playlistFile, episodeConfig)

            episodes = episodeConfig.episodes
            statusFilePath = os.path.join(episodes[0].base, self._config.statusFile)
            if os.path.isfile(statusFilePath):
                statusEpisodes = self._episodeService.load(statusFilePath)
                episodes = self._episodeService.matchEpisodes(statusEpisodes, episodes)
            self._episodeService.save(statusFilePath, episodes)
            self._view.episodeSelect.setEpisodes(episodes)
        except AttributeError:
            print("Skipping config save.")
