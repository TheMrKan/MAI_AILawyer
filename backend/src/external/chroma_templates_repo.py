import pydantic
from typing import Literal
import json

from src.core.templates.iface import TemplatesRepositoryABC
from src.core.templates.types import Template, FreeTemplate, StrictTemplate, StrictTemplateField
from src.external.base_chroma_repository import BaseChromaRepository


class _TemplateField(pydantic.BaseModel):
    key: str
    agent_instructions: str


class _TemplateMetadata(pydantic.BaseModel):
    type: Literal["free", "strict"]
    title: str
    storage_filename: str
    fields: str | None = None


class ChromaTemplatesRepository(BaseChromaRepository, TemplatesRepositoryABC):

    _COLLECTION_NAME = "templates"

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
            data = _TemplateMetadata(**meta)
            if data.type == "strict":
                obj = StrictTemplate(tpl_id, data.title, data.storage_filename, {})
                if data.fields:
                    fields = json.loads(data.fields)
                    for raw_field in fields:
                        field = _TemplateField(**raw_field)
                        obj.fields[field.key] = StrictTemplateField(field.key, field.agent_instructions)
            else:
                obj = FreeTemplate(tpl_id, data.title, data.storage_filename)

            result.append(obj)

        return result