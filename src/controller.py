from PyQt6.QtWidgets import QApplication

from models.app_config import AppConfig
from models.episode import Episode, EpisodeConfig
from models.page import Page
from services.directory_service import DirectoryService
from services.playlist_service import PlaylistService
from views.main_window import MainWindow


class QuickplayController:
    def __init__(
        self,
        config: AppConfig,
        view: MainWindow,
        directory_service: DirectoryService,
        playlist_service: PlaylistService,
    ) -> None:
        self._config = config
        self._view = view
        self._directory_service = directory_service
        self._playlist_service = playlist_service

        titles = self._directory_service.scan_titles(config.folderFile, config.extensions)
        self._view.titleSelect.setTitles(titles)

        self._connectSignals()

    def _connectSignals(self) -> None:
        self._view.titleSelect.titleSelected.connect(self._onTitleSelected)
        self._view.titleSelect.startPreviousClicked.connect(self._onStartPrevious)
        self._view.episodeSelect.backClicked.connect(self._onBackToTitles)
        self._view.episodeSelect.episodesSelected.connect(self._onEpisodesSelected)
        self._view.videoPlayer.stopRequested.connect(self._onStopPlayback)
        self._view.videoPlayer.player.quitEvent.connect(self._onStopPlayback)
        self._view.videoPlayer.player.isFullscreen.connect(self._onFullscreen)
        QApplication.instance().aboutToQuit.connect(self._saveConfig)

    def _onTitleSelected(self, base: str, name: str) -> None:
        episodes = self._directory_service.scan_episodes(base, name, self._config.extensions)
        self._view.episodeSelect.setEpisodes(episodes)
        self._view.setPage(Page.EPISODES)

    def _onStartPrevious(self) -> None:
        config = self._playlist_service.load(self._config.playlistFile)
        self._startPlayback(config)

    def _onEpisodesSelected(self, episodes: list[Episode]) -> None:
        config = EpisodeConfig(0, episodes)
        self._playlist_service.save(self._config.playlistFile, config)
        self._startPlayback(config)

    def _startPlayback(self, config: EpisodeConfig) -> None:
        self._view.videoPlayer.player.loadEpisodes(config)
        self._view.setPage(Page.PLAYER)
        self._view.videoPlayer.player.start()

    def _onStopPlayback(self) -> None:
        self._view.videoPlayer.player.stop()
        self._saveConfig()
        self._onFullscreen(False)
        if self._view.titleSelect.hasSelection():
            self._view.setPage(Page.EPISODES)
        else:
            self._view.setPage(Page.TITLES)

    def _onFullscreen(self, fullscreen: bool) -> None:
        if fullscreen:
            self._view.showFullScreen()
            self._view.videoPlayer.setControlsVisible(False)
        else:
            self._view.showNormal()
            self._view.videoPlayer.setControlsVisible(True)

    def _onBackToTitles(self) -> None:
        self._view.setPage(Page.TITLES)

    def _saveConfig(self) -> None:
        self._playlist_service.save(self._config.playlistFile, self._view.videoPlayer.player.episodeConfig)
