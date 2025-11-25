from dataclasses import dataclass

@dataclass
class Context:
    title: str
    alt_titles: list[str]
    description: str
    tags: list[str]
    publication_demographic: list[str]
    year: int