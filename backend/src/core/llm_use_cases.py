import json
from pydantic import BaseModel

from src.core.llm import AbstractLLM
from src.dto.messages import ChatMessage
from src.dto.laws import LawFragment


class ActsAnalysisResult(BaseModel):
    can_help: bool
    resume_for_user: str


class LLMUseCases:

    FIRST_SYSTEM_MESSAGE = ChatMessage.from_system(
        "Ты помогаешь пользователю составить юридически грамотную жалобу или обращение. "
        "Далее пользователь описывает проблему. "
        "Не нужно рассказывать о себе и говорить, какова твоя задача. Сразу переходи к сути.")

    ACTS_MESSAGE_TEMPLATE = "Вот такие правовые акты я нашел в своей базе: {acts}"

    ACTS_ANALYSIS_PROMPT = """
    Пиши так, будто акты нашел ты. Проанализируй их и дай очень краткое резюме ситуации.
    Сделай короткое заключение, можно ли помочь пользователю. Не давай инструкций, что ему делать.
    Оценивай строго, можно ли помочь пользователю в данной ситуации.
    Если помочь пользователю не получится, то так и скажи или предложи переформулировать проблему.
    Если помощь возможна, то спроси у пользователя подтверждение на продолжение. 
    Уточни, что сможешь поискать шаблоны обращение в своей базе и помочь с заполнением. ОБЯЗАТЕЛЬНО ВЕРНИ "can_help": 1, если это так.
    Дай ответ строго в формате JSON без лишних символов по примеру.
    Поля: 
    "can_help" - 0, если нарушения нет или помочь сложно. 1 - есть нарушение прав.
    "resume_for_user" - текстовый ответ для пользователя
    {
        "can_help": 0,
        "resume_for_user": "Ответ для пользователя"
    }
    """

    llm: AbstractLLM

    def __init__(self, llm: AbstractLLM):
        self.llm = llm

    def get_start_system_message(self):
        return self.FIRST_SYSTEM_MESSAGE

    def add_acts_to_dialogue(self, acts: list[LawFragment]):
        joined_acts = "\n\n".join([a.content for a in acts])
        return ChatMessage.from_ai(self.ACTS_MESSAGE_TEMPLATE.format(acts=joined_acts))

    async def analyze_acts_async(self, chat_history: list[ChatMessage]) -> ActsAnalysisResult:
        prompt = [ChatMessage.from_system(self.ACTS_ANALYSIS_PROMPT), *chat_history]
        ai_response = await self.llm.invoke_async(messages=prompt)

        # даст исключение, если формат не соблюден
        parsed = json.loads(ai_response.text)
        validated = ActsAnalysisResult(**parsed)

        return validated