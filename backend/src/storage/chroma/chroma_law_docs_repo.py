from src.core.laws.iface import LawDocsRepositoryABC
from src.core.laws.types import LawFragment
from src.storage.chroma.base_chroma_repository import BaseChromaRepository


class ChromaLawDocsRepository(BaseChromaRepository, LawDocsRepositoryABC):

    _COLLECTION_NAME = "laws"

    async def find_fragments_async(self, query: str) -> list[LawFragment]:
        query_result = await self._collection.query(query_texts=[query], n_results=5)
        result = []

        for frag_id, doc, meta in zip(query_result["ids"][0],
                                     query_result["documents"][0],
                                     query_result["metadatas"][0]):
            result.append(LawFragment(frag_id, meta["law_doc_id"], doc))

        return result

    async def list_fragments_async(self) -> list[LawFragment]:
        result = await self._collection.get(include=["documents", "metadatas"])
        fragments = []

        for frag_id, doc, meta in zip(result["ids"], result["documents"], result["metadatas"]):
            fragments.append(LawFragment(frag_id, meta["law_doc_id"], doc))

        return fragments

    async def add_of_update_fragment_async(self, fragment: LawFragment):
        await self._collection.upsert(
            ids=[fragment.fragment_id],
            documents=[fragment.content],
            metadatas=[{"law_doc_id": fragment.document_id}]
        )

    async def delete_fragment_async(self, fragment_id: str):
        await self._collection.delete(ids=[fragment_id])
