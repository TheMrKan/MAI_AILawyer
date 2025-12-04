from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver

from src.application.provider import Registerable, Provider, Singleton


class InMemorySaverWrapper(InMemorySaver, Registerable):
    __REG_ORDER__ = -1

    @classmethod
    async def on_build_provider(cls, provider: Provider):
        provider.register(BaseCheckpointSaver, Singleton(cls()))
