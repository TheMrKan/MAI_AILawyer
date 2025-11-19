from abc import ABC, abstractmethod
from typing import Iterable

from dto.messages import ChatMessage, MessageRole


class LLMABC(ABC):

    @abstractmethod
    async def invoke_async(self, messages: Iterable[ChatMessage], weak_model: bool = False) -> ChatMessage:
        pass
