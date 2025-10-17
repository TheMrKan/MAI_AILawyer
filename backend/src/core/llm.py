from abc import ABC, abstractmethod
from langchain_core.messages import AnyMessage, AIMessage
from typing import Iterable

from cerebras.cloud.sdk import AsyncCerebras
from cerebras.cloud.sdk.types.chat.chat_completion import ChatCompletionResponseChoiceMessage


class AbstractLLM(ABC):

    @abstractmethod
    async def invoke_async(self, messages: Iterable[AnyMessage]) -> AIMessage:
        pass



class CerebrasLLM(AbstractLLM):

    ROLES_MAP = {
        "system": "system",
        "human": "user",
        "ai": "assistant"
    }
    """
    LangChain : Cerebras
    """
    MODEL = "qwen-3-235b-a22b-thinking-2507"

    cerebras: AsyncCerebras

    def __init__(self):
        self.cerebras = AsyncCerebras()

    async def invoke_async(self, messages: Iterable[AnyMessage]) -> AIMessage:
        response = await self.cerebras.chat.completions.create(
            messages = [self.__serialize_message(m) for m in messages],
            model = self.MODEL
        )
        return self.__deserialize_ai_message(response.choices[0].message)

    @classmethod
    def __serialize_message(cls, message: AnyMessage) -> dict[str, object]:
        return {
            "content": message.content,
            "role": cls.ROLES_MAP[message.type],
        }

    @classmethod
    def __deserialize_ai_message(cls, message: ChatCompletionResponseChoiceMessage) -> AIMessage:
        assert message.role == "assistant", f"Invalid AI role: {message.role}"
        return AIMessage(message.content)