
from src.core.templates.iface import TemplatesRepositoryABC
from src.core.templates.types import Template


class TemplateManager:

    __repository: TemplatesRepositoryABC

    __FREE_TEMPLATE_ID = "free_template"

    def __init__(self, repository: TemplatesRepositoryABC):
        self.__repository = repository

    async def find_templates_async(self, query: str):
        return await self.__repository.find_templates_async(query, exclude_ids=[self.__FREE_TEMPLATE_ID])

    async def get_free_template_async(self) -> Template:
        return await self.__repository.get_template_async(self.__FREE_TEMPLATE_ID)

