from PyQt6.QtWidgets import QApplication

from models.app_config import AppConfig
from models.episode_config import EpisodeConfig
from models.page import Page
from models.title import Title
from services.config_service import ConfigService
from services.directory_service import DirectoryService
from services.update_service import UpdateService
from views.main_window import MainWindow


class QuickplayController:
    def __init__(self, view: MainWindow) -> None:
        self._view = view

        self._directoryService = DirectoryService()
        self._configService = ConfigService()
        self._updateService = UpdateService()

        self._config = self._configService.loadAppConfig()
        self._playlistConfig = self._configService.loadPlaylistConfig(self._config.playlistConfig)

        self._view.titleSelect.startPreviousDisabled.emit(len(self._playlistConfig.previous.episodes) <= 0)
        titles = self._directoryService.scanTitles(self._config.folders, self._config.extensions)
        self._view.titleSelect.setTitles(titles)
        self._view.settingsPage.setConfig(self._config)

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

        self._view.titleSelect.goToSettings.connect(self._onGoToSettings)
        self._view.settingsPage.settingsSaved.connect(self._onSettingsSaved)
        self._view.settingsPage.backClicked.connect(self._onBackToTitles)
        self._view.settingsPage.checkForUpdates.connect(self._onCheckForUpdates)
        self._view.settingsPage.downloadUpdate.connect(self._onDownloadUpdate)
        self._view.settingsPage.installUpdate.connect(self._onInstallUpdate)

        self._updateService.updateAvailable.connect(self._onUpdateAvailable)
        self._updateService.noUpdate.connect(self._onNoUpdate)
        self._updateService.checkError.connect(self._onUpdateError)
        self._updateService.downloadProgress.connect(self._view.settingsPage.setDownloadProgress)
        self._updateService.downloadComplete.connect(self._onDownloadComplete)
        self._updateService.downloadError.connect(self._onUpdateError)

    def _savePlaylistConfig(self) -> None:
        self._configService.savePlaylistConfig(self._config.playlistConfig, self._playlistConfig)

    def _onTitleSelected(self, title: Title) -> None:
        episodes = self._directoryService.scanEpisodes(title, self._config.extensions)
        episodeConfig = self._playlistConfig.updateTitles(title, EpisodeConfig(0, episodes))
        self._savePlaylistConfig()
        self._view.episodeSelect.setEpisodes(episodeConfig)
        self._view.setPage(Page.EPISODES)

    def _onStartPrevious(self) -> None:
        self._startPlayback(self._playlistConfig.previous)

    def _onEpisodesSelected(self, episodeConfig: EpisodeConfig) -> None:
        self._playlistConfig.updatePrevious(episodeConfig)
        self._savePlaylistConfig()
        self._view.titleSelect.startPreviousDisabled.emit(False)
        self._startPlayback(self._playlistConfig.previous)

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

    def _onGoToSettings(self) -> None:
        self._view.setPage(Page.SETTINGS)

    def _onBackToTitles(self) -> None:
        self._view.setPage(Page.TITLES)

    def _onSettingsSaved(self, updatedConfig: AppConfig) -> None:
        self._config.folders = updatedConfig.folders
        self._config.extensions = updatedConfig.extensions
        self._configService.saveAppConfig(self._config)

        titles = self._directoryService.scanTitles(self._config.folders, self._config.extensions)
        self._view.titleSelect.setTitles(titles)

    def _onCheckForUpdates(self) -> None:
        self._view.settingsPage.setUpdateStatus("Checking for updates...")
        self._updateService.checkForUpdate()

    def _onUpdateAvailable(self, version: str, _assetUrl: str) -> None:
        self._view.settingsPage.setUpdateStatus(f"New version available: {version}")
        self._view.settingsPage.setDownloadAvailable(True)

    def _onNoUpdate(self) -> None:
        self._view.settingsPage.setUpdateStatus("You are up to date.")

    def _onUpdateError(self, message: str) -> None:
        self._view.settingsPage.setUpdateStatus(message)

    def _onDownloadUpdate(self) -> None:
        self._view.settingsPage.setUpdateStatus("Downloading update...")
        self._updateService.downloadUpdate()

    def _onDownloadComplete(self, _zipPath: str) -> None:
        self._view.settingsPage.setUpdateStatus("Download complete. Click the button to apply.")
        self._view.settingsPage.setInstallReady(True)

    def _onInstallUpdate(self) -> None:
        self._view.settingsPage.setUpdateStatus("Installing update...")
        self._updateService.installUpdate()

    def _saveConfig(self) -> None:
        try:
            episodeConfig = self._view.playerPage.player.episodeConfig
            self._playlistConfig.updatePrevious(episodeConfig)
            self._view.titleSelect.startPreviousDisabled.emit(False)

            episodeConfig = self._playlistConfig.updateTitles(episodeConfig.episodes[0].title, episodeConfig)
            self._savePlaylistConfig()
            self._view.episodeSelect.setEpisodes(episodeConfig)
        except AttributeError:
            print("Skipping config save.")
