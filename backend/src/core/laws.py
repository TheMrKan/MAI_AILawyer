from abc import ABC, abstractmethod

from dto.laws import LawFragment


class LawDocsRepositoryABC(ABC):

    @abstractmethod
    async def find_fragments_async(self, query: str) -> list[LawFragment]:
        pass

    @abstractmethod
    async def list_fragments_async(self) -> list[LawFragment]:
        pass

    @abstractmethod
    async def add_of_update_fragment_async(self, fragment: LawFragment):
        pass

    @abstractmethod
    async def delete_fragment_async(self, fragment_id: str):
        pass