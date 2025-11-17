
from src.core.templates.iface import TemplatesRepositoryABC


class TemplateService:

    __repository: TemplatesRepositoryABC

    __FREE_TEMPLATE_ID = "free_template"

    def __init__(self, repository: TemplatesRepositoryABC):
        self.__repository = repository

    async def find_templates_async(self, query: str):
        return await self.__repository.find_templates_async(query, exclude_ids=[self.__FREE_TEMPLATE_ID])

