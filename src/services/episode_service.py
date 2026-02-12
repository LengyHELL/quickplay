import simplejson as json

from models.episode import Episode


class EpisodeService:
    def load(self, path: str) -> list[Episode]:
        with open(path, "r", encoding="utf-8") as file:
            data = json.loads(file.read())
            return [Episode(**e) for e in data]

    def save(self, path: str, episodes: list[Episode]) -> None:
        with open(path, "w", encoding="utf-8") as file:
            data = [e.__dict__ for e in episodes]
            file.write(json.dumps(data, indent=2))

    def matchEpisodes(self, base: list[Episode], status: list[Episode]) -> list[Episode]:
        matched: list[Episode] = []

        for b in base:
            try:
                index = [s.path for s in status].index(b.path)
                matched.append(status[index])
            except ValueError:
                matched.append(b)

        return matched
