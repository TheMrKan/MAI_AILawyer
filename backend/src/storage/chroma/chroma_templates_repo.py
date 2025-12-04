import pydantic
from typing import Literal
import json
import chromadb

from src.core.templates.iface import TemplatesRepositoryABC
from src.core.templates.types import Template, TemplateField
from src.storage.chroma.base_chroma_repository import BaseChromaRepository
from src.application.provider import Registerable, Singleton, Provider


class _TemplateField(pydantic.BaseModel):
    key: str
    agent_instructions: str


class _TemplateMetadata(pydantic.BaseModel):
    type: Literal["free", "strict"]
    title: str
    storage_filename: str
    fields: str | None = None


class ChromaTemplatesRepository(BaseChromaRepository, TemplatesRepositoryABC, Registerable):

    @classmethod
    async def on_build_provider(cls, provider: Provider):
        client = provider[chromadb.AsyncClientAPI]
        templates_repo = cls(client)
        await templates_repo.init_async()
        provider.register(TemplatesRepositoryABC, Singleton(templates_repo))

    _COLLECTION_NAME = "templates"

    @staticmethod
    def __from_db_type(tpl_id: str, metadata: dict) -> Template:
        data = _TemplateMetadata(**metadata)
        obj = Template(tpl_id, data.title, data.storage_filename, {})
        if data.fields:
            fields = json.loads(data.fields)
            for raw_field in fields:
                field = _TemplateField(**raw_field)
                obj.fields[field.key] = TemplateField(field.key, field.agent_instructions)
        return obj

    async def get_template_async(self, tpl_id: str) -> Template:
        query_result = await self._collection.get(ids=[tpl_id])
        if not any(query_result["ids"]):
            raise KeyError(tpl_id)

        return self.__from_db_type(query_result["ids"][0], query_result["metadatas"][0])

    async def find_templates_async(self, query: str, exclude_ids: list[str] | None = None) -> list[Template]:
        where = None
        if exclude_ids:
            where = {
                "ids": {
                    "$nin": exclude_ids
                }
            }
        query_result = await self._collection.query(query_texts=[query], n_results=3, where=where)
        result = []

        for tpl_id, meta in zip(query_result["ids"][0],
                                query_result["metadatas"][0]):
            result.append(self.__from_db_type(tpl_id, meta))

        return result
