from abc import ABC, abstractmethod
from typing import Iterable

from src.core.chats.types import ChatMessage


class LLMABC(ABC):

    @abstractmethod
    async def invoke_async(self, messages: Iterable[ChatMessage], weak_model: bool = False, json_output: bool = False) -> ChatMessage:
        pass
