from abc import ABC, abstractmethod
from typing import Iterable
from cerebras.cloud.sdk import AsyncCerebras
from cerebras.cloud.sdk.types.chat.chat_completion import ChatCompletionResponseChoiceMessage

from src.dto.messages import ChatMessage, MessageRole


class AbstractLLM(ABC):

    @abstractmethod
    async def invoke_async(self, messages: Iterable[ChatMessage]) -> ChatMessage:
        pass



class CerebrasLLM(AbstractLLM):

    ROLES_MAP = {
        MessageRole.SYSTEM: "system",
        MessageRole.USER: "user",
        MessageRole.AI: "assistant"
    }

    MODEL = "qwen-3-235b-a22b-thinking-2507"

    cerebras: AsyncCerebras

    def __init__(self):
        self.cerebras = AsyncCerebras()

    async def invoke_async(self, messages: Iterable[ChatMessage]) -> ChatMessage:
        response = await self.cerebras.chat.completions.create(
            messages = [self.__serialize_message(m) for m in messages],
            model = self.MODEL
        )
        return self.__deserialize_ai_message(response.choices[0].message)

    @classmethod
    def __serialize_message(cls, message: ChatMessage) -> dict[str, object]:
        return {
            "content": message.text,
            "role": cls.ROLES_MAP[message.role],
        }

    @classmethod
    def __deserialize_ai_message(cls, message: ChatCompletionResponseChoiceMessage) -> ChatMessage:
        assert message.role == "assistant", f"Invalid AI role: {message.role}"
        return ChatMessage.from_ai(message.content)