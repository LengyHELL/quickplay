import os
import subprocess
import sys
import tempfile
import zipfile
from urllib.error import URLError
from urllib.request import Request, urlopen

import simplejson as json
from PyQt6.QtCore import QObject, QThread, pyqtSignal

from _version import VERSION

GITHUB_REPO = "LengyHELL/quickplay"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

DOWNLOAD_CHUNK_SIZE = 65536


class _CheckWorker(QObject):
    updateAvailable = pyqtSignal(str, str)
    "version, assetUrl"
    noUpdate = pyqtSignal()
    error = pyqtSignal(str)
    "error"

    def run(self) -> None:
        if not GITHUB_REPO:
            self.error.emit("GitHub repository is not configured.")
            return

        try:
            request = Request(GITHUB_API_URL, headers={"Accept": "application/vnd.github.v3+json"})
            with urlopen(request, timeout=15) as response:
                data = json.loads(response.read().decode())

            latestVersion: str = data.get("tag_name", "")
            if not latestVersion:
                self.error.emit("Could not determine latest version.")
                return

            if latestVersion == VERSION:
                self.noUpdate.emit()
                return

            assets: list[dict] = data.get("assets", [])
            zipAsset = next((a for a in assets if a["name"].endswith(".zip")), None)
            if not zipAsset:
                self.error.emit(f"Version {latestVersion} has no .zip asset.")
                return

            self.updateAvailable.emit(latestVersion, zipAsset["browser_download_url"])

        except (URLError, json.JSONDecodeError, KeyError) as e:
            self.error.emit(f"Failed to check for updates: {e}")


class _DownloadWorker(QObject):
    progress = pyqtSignal(int)
    "percentage"
    complete = pyqtSignal(str)
    "zipPath"
    error = pyqtSignal(str)
    "error"

    def __init__(self, url: str) -> None:
        super().__init__()
        self._url = url

    def run(self) -> None:
        try:
            request = Request(self._url)
            with urlopen(request, timeout=60) as response:
                totalSize = int(response.headers.get("Content-Length", 0))
                downloaded = 0

                tmpDir = tempfile.mkdtemp(prefix="quickplay_update_")
                zipPath = os.path.join(tmpDir, "update.zip")

                with open(zipPath, "wb") as f:
                    while True:
                        chunk = response.read(DOWNLOAD_CHUNK_SIZE)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if totalSize > 0:
                            self.progress.emit(int(downloaded * 100 / totalSize))

            self.complete.emit(zipPath)

        except (URLError, OSError) as e:
            self.error.emit(f"Download failed: {e}")


class UpdateService(QObject):
    updateAvailable = pyqtSignal(str, str)
    "version, assetUrl"
    noUpdate = pyqtSignal()
    checkError = pyqtSignal(str)
    "error"
    downloadProgress = pyqtSignal(int)
    "percentage"
    downloadComplete = pyqtSignal(str)
    "zipPath"
    downloadError = pyqtSignal(str)
    "error"

    def __init__(self) -> None:
        super().__init__()
        self._checkThread: QThread | None = None
        self._downloadThread: QThread | None = None
        self._latestAssetUrl: str = ""
        self._downloadedZipPath: str = ""

    def checkForUpdate(self) -> None:
        if self._checkThread and self._checkThread.isRunning():
            return

        self._checkThread = QThread()
        self._checkWorker = _CheckWorker()
        self._checkWorker.moveToThread(self._checkThread)

        self._checkThread.started.connect(self._checkWorker.run)
        self._checkWorker.updateAvailable.connect(self._onUpdateAvailable)
        self._checkWorker.noUpdate.connect(self.noUpdate)
        self._checkWorker.error.connect(self.checkError)

        self._checkWorker.updateAvailable.connect(lambda *_: self._checkThread.quit())
        self._checkWorker.noUpdate.connect(self._checkThread.quit)
        self._checkWorker.error.connect(lambda _: self._checkThread.quit())

        self._checkThread.start()

    def _onUpdateAvailable(self, version: str, assetUrl: str) -> None:
        self._latestAssetUrl = assetUrl
        self.updateAvailable.emit(version, assetUrl)

    def downloadUpdate(self) -> None:
        if not self._latestAssetUrl:
            return
        if self._downloadThread and self._downloadThread.isRunning():
            return

        self._downloadThread = QThread()
        self._downloadWorker = _DownloadWorker(self._latestAssetUrl)
        self._downloadWorker.moveToThread(self._downloadThread)

        self._downloadThread.started.connect(self._downloadWorker.run)
        self._downloadWorker.progress.connect(self.downloadProgress)
        self._downloadWorker.complete.connect(self._onDownloadComplete)
        self._downloadWorker.error.connect(self.downloadError)

        self._downloadWorker.complete.connect(lambda _: self._downloadThread.quit())
        self._downloadWorker.error.connect(lambda _: self._downloadThread.quit())

        self._downloadThread.start()

    def _onDownloadComplete(self, zipPath: str) -> None:
        self._downloadedZipPath = zipPath
        self.downloadComplete.emit(zipPath)

    def installUpdate(self) -> None:
        if not self._downloadedZipPath or not os.path.isfile(self._downloadedZipPath):
            return

        appDir = os.path.dirname(sys.executable)
        extractDir = tempfile.mkdtemp(prefix="quickplay_extract_")

        with zipfile.ZipFile(self._downloadedZipPath, "r") as zf:
            zf.extractall(extractDir)

        # Find the inner directory (e.g., extractDir/quickplay/...)
        entries = os.listdir(extractDir)
        sourceDir = os.path.join(extractDir, entries[0]) if len(entries) == 1 else extractDir

        # Write a batch script that replaces the app files after exit
        scriptPath = os.path.join(tempfile.gettempdir(), "quickplay_update.bat")
        with open(scriptPath, "w") as f:
            f.write("@echo off\n")
            f.write("timeout /t 2 /nobreak >nul\n")
            f.write(f'xcopy /s /e /y "{sourceDir}\\*" "{appDir}\\"\n')
            f.write(f'rmdir /s /q "{extractDir}"\n')
            f.write(f'del "{self._downloadedZipPath}"\n')
            f.write(f'start "" "{os.path.join(appDir, "quickplay.exe")}"\n')
            f.write('del "%~f0"\n')

        subprocess.Popen(
            ["cmd", "/c", scriptPath],
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
        )

        QThread.msleep(200)
        sys.exit(0)
