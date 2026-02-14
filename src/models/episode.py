from dataclasses import dataclass

from models.title import Title


@dataclass
class Episode:
    name: str
    path: str
    title: Title
    progress: float
    completed: bool

    @classmethod
    def fromDict(cls, data: dict) -> "Episode":
        return cls(data["name"], data["path"], Title.fromDict(data["title"]), data["progress"], data["completed"])
