import json
from pydantic import BaseModel
from dataclasses import dataclass
from typing import NamedTuple

from src.core.llm import LLMABC
from src.dto.messages import ChatMessage
from src.dto.laws import LawFragment
from src.core.templates.types import Template


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


__TEMPLATES_ANALYSIS_MESSAGE = ChatMessage.from_system("""
Выше даны тексты шаблонов документов для анализа. 
Твоя задача - определить, какой шаблон обращение больше всего подходит к описанной ситуации.
Если считаешь, что ни один шаблон не подходит, то нужно это явно обозначить. Сообщи пользователю, что не нашел подходящего шаблона и можешь составить обращение в свободной форме.
Не упоминай шаблоны, которые не подходят к данной ситуации.
Также дай краткое описание шаблона для пользователя и спроси, устраивает ли его этот шаблон и хочет ли он продолжить работу.
Текст для пользователя может выглядить подобным образом: "Я нашел подходящий шаблон в своей базе: <описание шаблона>"
Шаблоны нумеруются с нуля сверху вниз. Номер подходящего шаблона укажи в поле "relevant_template_index". Если нет подходящего шаблона, то укажи -1 в этом поле.
Ответ дай в формате JSON строго по заданной схеме без лишнего текста:
{
    "relevant_template_index": 0,
    "user_message": "Текст ответа для пользователя"
}
""")


class __TemplatesAnalysisLLMResponseSchema(BaseModel):
    relevant_template_index: int
    user_message: str


class TemplatesAnalysisResult(NamedTuple):
    relevant_template_index: int | None
    user_message: ChatMessage


async def analyze_templates_async(llm: LLMABC,
                             chat_history: list[ChatMessage],
                             template_texts: list[str]) -> TemplatesAnalysisResult:
    prompt = [*chat_history]
    for text in template_texts:
        prompt.append(ChatMessage.from_system(text))
    prompt.append(__TEMPLATES_ANALYSIS_MESSAGE)

    ai_reponse = await llm.invoke_async(messages=prompt)
    # даст исключение, если формат не соблюден
    parsed = json.loads(ai_reponse.text)
    validated = __TemplatesAnalysisLLMResponseSchema(**parsed)

    index = validated.relevant_template_index if validated.relevant_template_index >= 0 else None
    return TemplatesAnalysisResult(index, ChatMessage.from_ai(validated.user_message))


__FREE_TEMPLATE_SETUP_TEXT = """
Теперь ты должен оставить обращение в свободной форме. Выше дан текст шаблона. У обращения есть несколько обязательных полей, которые тебе нужно заполнить:
{fields}
В поле с основным содержимым ты должен вписать текст обращения.
Задавай пользователю вопросы до тех пор, пока информации не будет достаточно для составления текста. Веди с ним диалог.
Твой ответ должен быть строго в JSON формате.
"user_message" - это текст вопроса, который нужно задать пользователю.
"is_ready" - bool флаг, показывающий, достаточно ли сейчас информации. Когда информации будет достаточно, верни "is_ready" = true. Тогда "user_message" оставь пустым.
{{
    "user_message": "Вопрос пользователю?",
    "is_ready": false
}}
"""


def setup_free_template_loop(free_template: Template, free_template_text: str) -> list[ChatMessage]:
    rendered_fields = "\n".join(f"{f.key} - {f.agent_instructions}" for f in free_template.fields.values())
    return [
        ChatMessage.from_system(free_template_text),
        ChatMessage.from_system(__FREE_TEMPLATE_SETUP_TEXT.format(fields=rendered_fields))
    ]
