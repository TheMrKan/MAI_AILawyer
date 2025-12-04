import chromadb

from src.application.provider import Registerable, Singleton, Provider


class ConnectionRegistrator(Registerable):
    __REG_ORDER__ = -1

    @classmethod
    async def on_build_provider(cls, provider: Provider):
        chroma_client = await chromadb.AsyncHttpClient(host="chroma", port=8000)
        provider.register(chromadb.AsyncClientAPI, Singleton(chroma_client))
