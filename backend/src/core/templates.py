from abc import ABC, abstractmethod

from src.dto.templates import Template


class TemplatesRepositoryABC(ABC):

    @abstractmethod
    async def find_templates_async(self, query: str) -> list[Template]:
        pass