import logging

import chromadb

from src.core.laws import LawDocsRepositoryABC
from src.dto.laws import LawFragment


class ChromaLawDocsRepository(LawDocsRepositoryABC):

    __COLLECTION_NAME = "laws"

    __host: str
    __port: int
    __client: chromadb.AsyncClientAPI
    __collection: chromadb.api.models.AsyncCollection.AsyncCollection
    __logger: logging.Logger

    def __init__(self, host: str, port: int):
        self.__host = host
        self.__port = port
        self.__logger = logging.getLogger(self.__class__.__name__)

    async def init_async(self):
        self.__client = await chromadb.AsyncHttpClient(host=self.__host, port=self.__port)
        self.__collection = await self.__client.get_or_create_collection(self.__COLLECTION_NAME)

    async def find_fragments_async(self, query: str) -> list[LawFragment]:
        query_result = await self.__collection.query(query_texts=[query], n_results=5)
        result = []

        for frag_id, doc, dst, meta in zip(query_result["ids"][0],
                                     query_result["documents"][0],
                                     query_result["distances"][0],
                                     query_result["metadatas"][0]):
            result.append(LawFragment(frag_id, meta["law_doc_id"], doc, dst))

        return result

