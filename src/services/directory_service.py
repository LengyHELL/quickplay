import os

from models.episode import Episode


class DirectoryService:
    def scan_titles(self, folderFile: str, extensions: list[str]) -> list[tuple[str, str]]:
        titles: list[tuple[str, str]] = []

        if not os.path.isfile(folderFile):
            print(f"Failed to open folder file '{folderFile}'!")
            return titles

        with open(folderFile, "r", encoding="utf-8") as file:
            folders = [f.strip() for f in file.readlines()]
            for f in folders:
                if not os.path.isdir(f):
                    print(f"Failed to find directory '{f}'!")
                    continue

                dirs = os.listdir(f)
                for d in dirs:
                    path = os.path.join(f, d)
                    if os.path.isdir(path) and any(
                        os.path.isfile(os.path.join(path, entry)) and os.path.splitext(entry)[1] in extensions
                        for entry in os.listdir(path)
                    ):
                        titles.append((f, d))

        return titles

    def scan_episodes(self, base: str, title: str, extensions: list[str]) -> list[Episode]:
        episodes: list[Episode] = []
        directory = os.path.join(base, title)

        if not os.path.isdir(directory):
            print(f"Failed to find directory '{directory}'!")
            return episodes

        dirs = os.listdir(directory)
        for d in dirs:
            if os.path.isfile(os.path.join(directory, d)) and os.path.splitext(d)[-1] in extensions:
                episodes.append(Episode(d, os.path.join(directory, d), 0.0, False))

        return episodes
