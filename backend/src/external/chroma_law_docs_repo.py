import logging

from src.core.laws import LawDocsRepositoryABC
from src.dto.laws import LawFragment
from src.external.base_chroma_repository import BaseChromaRepository


class ChromaLawDocsRepository(BaseChromaRepository, LawDocsRepositoryABC):

    _COLLECTION_NAME = "laws"

    async def find_fragments_async(self, query: str) -> list[LawFragment]:
        query_result = await self._collection.query(query_texts=[query], n_results=5)
        result = []

        for frag_id, doc, dst, meta in zip(query_result["ids"][0],
                                     query_result["documents"][0],
                                     query_result["distances"][0],
                                     query_result["metadatas"][0]):
            result.append(LawFragment(frag_id, meta["law_doc_id"], doc, dst))

        return result

