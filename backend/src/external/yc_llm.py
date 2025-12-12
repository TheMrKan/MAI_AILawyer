from typing import Iterable, TYPE_CHECKING
import os
import logging

from yandex_cloud_ml_sdk import AsyncYCloudML
from yandex_cloud_ml_sdk._models import AsyncCompletions
from yandex_cloud_ml_sdk._models.completions.result import Alternative

from src.core.chats.types import ChatMessage, MessageRole
from src.core.llm.iface import LLMABC
from src.application.provider import Registerable, Provider, Singleton


class YandexCloudLLM(LLMABC, Registerable):

    @classmethod
    async def on_build_provider(cls, provider: Provider):
        provider.register(LLMABC, Singleton(cls()))

    __cloud: "AsyncYCloudML"
    __model_strong: "AsyncCompletions"
    __model_weak: "AsyncCompletions"
    __logger: logging.Logger

    MODEL_STRONG = ("yandexgpt", "rc")
    MODEL_WEAK = ("yandexgpt-lite", "latest")

    ROLES_MAP = {
        MessageRole.SYSTEM: "system",
        MessageRole.USER: "user",
        MessageRole.AI: "assistant"
    }

    def __init__(self):
        self.__logger = logging.getLogger(type(self).__name__)

        auth = os.getenv("YC_AUTH_TOKEN")
        folder = os.getenv("YC_FOLDER")
        if not auth or not folder:
            raise RuntimeError("YC_AUTH_TOKEN or YC_FOLDER is not configured")

        self.__cloud = AsyncYCloudML(folder_id=folder, auth=auth)
        self.__model_strong = self.__cloud.models.completions(model_name=self.MODEL_STRONG[0], model_version=self.MODEL_STRONG[1])
        self.__model_weak = self.__cloud.models.completions(model_name=self.MODEL_WEAK[0], model_version=self.MODEL_WEAK[1])

    async def invoke_async(self,
                           messages: Iterable[ChatMessage],
                           weak_model: bool = False,
                           json_output: bool = False) -> ChatMessage:

        model = self.__model_weak if weak_model else self.__model_strong
        if json_output:
            model = model.configure(response_format="json")

        self.__logger.debug("LLM Prompt (model: %s):\n%s", "WEAK" if weak_model else "STRONG", "\n".join(repr(m) for m in messages))

        serialized_messages = [self.__serialize_message(m) for m in messages]

        kwargs = {}
        if json_output:
            kwargs["response_format"] = {"type": "json_object"}

        response = await model.run(serialized_messages)
        self.__logger.debug("LLM Response (tokens: %s/%s/%s):\n%s",
                            response.usage.input_text_tokens,
                            response.usage.completion_tokens,
                            response.usage.total_tokens,
                            response.alternatives[0].text)

        return self.__deserizlize_message(response.alternatives[0])

    @classmethod
    def __serialize_message(cls, message: ChatMessage) -> dict[str, object]:
        return {
            "text": message.text,
            "role": cls.ROLES_MAP[message.role],
        }

    @classmethod
    def __deserizlize_message(cls, model_message: "Alternative") -> ChatMessage:
        assert model_message.role == "assistant"
        text = model_message.text
        think_end = text.find("</think>")
        if think_end != -1:
            text = text[think_end + len("</think>"):]

        json_start, json_end = text.find("{"), text.rfind("}")
        if json_start != -1 and json_end != -1:
            text = text[json_start:json_end + 1]

        return ChatMessage.from_ai(text)
