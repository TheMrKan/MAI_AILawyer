import json
from pydantic import BaseModel
from dataclasses import dataclass

from src.core.llm import LLMABC
from src.dto.messages import ChatMessage
from src.dto.laws import LawFragment


@dataclass
class ActsAnalysisResult:
    can_help: bool
    messages: list[ChatMessage]


class __ActsAnalysisLLMResponseSchema(BaseModel):
    can_help: bool
    resume_for_user: str


__FIRST_SYSTEM_MESSAGE = ChatMessage.from_system(
    "Ты помогаешь пользователю составить юридически грамотную жалобу или обращение. "
    "Далее пользователь описывает проблему. "
    "Не нужно рассказывать о себе и говорить, какова твоя задача. Сразу переходи к сути.")


def get_start_system_message():
    return __FIRST_SYSTEM_MESSAGE


__ACTS_MESSAGE_TEMPLATE = "Вот такие правовые акты я нашел в своей базе: {acts}"


__ACTS_ANALYSIS_MESSAGE = ChatMessage.from_system("""
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
""")



async def analyze_acts_async(llm: LLMABC,
                             chat_history: list[ChatMessage],
                             law_docs: list[LawFragment]) -> ActsAnalysisResult:
    joined_acts = "\n\n".join([a.content for a in law_docs])
    documents_message = ChatMessage.from_ai(__ACTS_MESSAGE_TEMPLATE.format(acts=joined_acts))

    prompt = [documents_message, __ACTS_ANALYSIS_MESSAGE, *chat_history]
    ai_response = await llm.invoke_async(messages=prompt)

    # даст исключение, если формат не соблюден
    parsed = json.loads(ai_response.text)
    validated = __ActsAnalysisLLMResponseSchema(**parsed)
    new_messages = [documents_message, ChatMessage.from_ai(validated.resume_for_user)]

    return ActsAnalysisResult(can_help=validated.can_help, messages=new_messages)


__CHECK_AGREEMENT_MESSAGE = ChatMessage.from_system("""
Оцени, является ли это согласием продолжить работу. Верни только одну цифру без дополнительных комментариев.
Пример положительный (если пользователь желает продолжить диалог):
1
Пример отрицательный:
0
""")

async def is_agreement_async(llm: LLMABC, message: ChatMessage) -> bool:
    ai_response = await llm.invoke_async(weak_model=True, messages=[__CHECK_AGREEMENT_MESSAGE, message])
    return "1" in ai_response.text