from dataclasses import dataclass


@dataclass
class Title:
    name: str
    base: str

    @classmethod
    def fromDict(cls, data: dict) -> "Title":
        return cls(**data)
