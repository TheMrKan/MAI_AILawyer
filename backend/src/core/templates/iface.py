from abc import ABC, abstractmethod
from typing import BinaryIO

from src.core.templates.types import Template


class TemplatesRepositoryABC(ABC):

    @abstractmethod
    async def find_templates_async(self, query: str, exclude_id: list[str] | None = None) -> list[Template]:
        pass


class TemplatesFileStorageABC(ABC):

    @abstractmethod
    def open_template_file(self, filename: str) -> BinaryIO:
        pass
