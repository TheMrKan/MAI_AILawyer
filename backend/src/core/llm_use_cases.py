from src.core.llm import AbstractLLM
from src.dto.messages import ChatMessage


class LLMUseCases:

    FIRST_SYSTEM_MESSAGE = ChatMessage.from_system(
        "Ты помогаешь пользователю составить юридически грамотную жалобу или обращение. "
        "Далее пользователь опишет проблему. "
        "Не нужно рассказывать о себе и говорить, какова твоя задача. Сразу переходи к сути.")

    ACTS_ANALYSIS_PROMPT = \
        ("В базе нашлись следующие правовые акты на эту тему: {acts}."
         "Проанализируй их и дай краткое резюме для пользователя.")


    llm: AbstractLLM

    def __init__(self, llm: AbstractLLM):
        self.llm = llm

    async def analyze_first_description_async(self, user_description: ChatMessage) -> ChatMessage:
        prompt = [self.FIRST_SYSTEM_MESSAGE, user_description]

        ai_response = await self.llm.invoke_async(messages=prompt)

        return ai_response

    async def analyze_acts_async(self, chat_history: list[ChatMessage], acts: list[str]) -> ChatMessage:
        instructions = ChatMessage.from_system(self.ACTS_ANALYSIS_PROMPT.format(acts=acts))
        prompt = chat_history + [instructions]

        ai_response = await self.llm.invoke_async(messages=prompt)

        return ai_response