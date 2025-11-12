from dataclasses import dataclass


@dataclass(frozen=True)
class LawFragment:
    fragment_id: str
    document_id: str
    content: str
    distance: float

