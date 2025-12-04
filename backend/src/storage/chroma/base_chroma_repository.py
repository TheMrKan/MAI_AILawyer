import chromadb
import logging


class BaseChromaRepository:

    _COLLECTION_NAME = ""

    __client: chromadb.AsyncClientAPI
    _collection: chromadb.api.models.AsyncCollection.AsyncCollection
    _logger: logging.Logger

    def __init__(self, client: chromadb.AsyncClientAPI):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.__client = client

    async def init_async(self):
        self._collection = await self.__client.get_or_create_collection(self._COLLECTION_NAME)