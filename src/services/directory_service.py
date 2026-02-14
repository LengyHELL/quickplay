import os

from models.episode import Episode
from models.title import Title


class DirectoryService:
    def scanTitles(self, folders: list[str], extensions: list[str]) -> list[Title]:
        titles: list[Title] = []

        for folder in folders:
            if not os.path.isdir(folder):
                print(f"Failed to find directory '{folder}'!")
                continue

            directories = os.listdir(folder)

            for directory in directories:
                path = os.path.join(folder, directory)

                if os.path.isdir(path) and any(
                    os.path.isfile(os.path.join(path, entry)) and os.path.splitext(entry)[1] in extensions
                    for entry in os.listdir(path)
                ):
                    titles.append(Title(directory, folder))

        return titles

    def scanEpisodes(self, title: Title, extensions: list[str]) -> list[Episode]:
        episodes: list[Episode] = []
        path = os.path.join(title.base, title.name)

        if not os.path.isdir(path):
            print(f"Failed to find directory '{path}'!")
            return episodes

        directories = os.listdir(path)
        for directory in directories:
            if os.path.isfile(os.path.join(path, directory)) and os.path.splitext(directory)[-1] in extensions:
                episodes.append(Episode(directory, os.path.join(path, directory), title, 0.0, False))

        return episodes
