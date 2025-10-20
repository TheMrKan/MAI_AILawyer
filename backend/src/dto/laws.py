from dataclasses import dataclass


@dataclass(frozen=True)
class LawFragment:
    source_document: int
    content: str
