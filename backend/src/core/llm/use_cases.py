import json
from pydantic import BaseModel
from dataclasses import dataclass
from typing import NamedTuple

from src.core.llm import LLMABC
from src.core.chats.types import ChatMessage
from src.core.laws.types import LawFragment
from src.core.templates.types import Template


__FIRST_SYSTEM_MESSAGE = ChatMessage.from_system("""
Ты помогаешь пользователю составить юридически грамотную жалобу или обращение.
Не нужно рассказывать о себе и говорить, какова твоя задача. Сразу переходи к сути.
Далее пользователь описывает проблему. Тебе нужно решить, достаточно ли информаци для того, чтобы перейти к поиску правовых актов.
Если информации недостаточно, то задай уточняющий вопрос. Старайся задавать короткие вопросы: один пункт за вопрос.
Пока не принимай решения о том, можно ли помочь пользователю.
Это решение ты должен будешь принять на следующем этапе после поиска подходящих правовых актов.
Если считаешь, что нарушения скорее всего нет, то сразу переходи к поиску актов.
Дай ответ строго в формате JSON без лишних символов по примеру без какого либо форматирования. Чистый JSON файл.
НИ В КОЕМ СЛУЧАЕ НН ПЕРЕСТАВАЙ ОТВЕЧАТЬ В JSON, ПОКА НЕ БУДЕТ НОВЫХ СИСТЕМНЫХ ИНСТРУКЦИЙ.
Поля:
"is_ready" - 0, пока информации недостаточно. 1 - можно переходить на следующий этап поиска правовых актов.
"user_message" - уточняющий вопрос для пользователя, если информации недостаточно. Оставь пустым, если переходим к следующему этапу.
{
"is_ready": 0,
"user_message": "Уточняющий вопрос?"
}
""")


def get_start_system_message():
    return __FIRST_SYSTEM_MESSAGE


class __InfoAnalysisLLMResponseSchema(BaseModel):
    is_ready: bool
    user_message: str


class InfoAnalysisResult(NamedTuple):
    is_ready_to_continue: bool
    user_message: str


async def analyze_first_info_async(llm: LLMABC,
                                   chat_history: list[ChatMessage]) -> InfoAnalysisResult:

    ai_response = await llm.invoke_async(messages=chat_history, json_output=True)
    # даст исключение, если формат не соблюден
    parsed = json.loads(ai_response.text)
    validated = __InfoAnalysisLLMResponseSchema(**parsed)

    return InfoAnalysisResult(validated.is_ready, validated.user_message)


PREPARE_LAWS_QUERY_PROMPT = ChatMessage.from_system("""
На основе предыдущих сообщений составь поисковый запрос для векторной базы правовых актов. Запрос будет векторизован для поиска ближайших совпадений.
Используется слабый векторайзер, постарайся использовать слова, которые будут в статьях, чтобы он точно зацепился.
Нужно получить наиболее релевантные статьи кодекса. Верни только текст запроса без лишних комментариев.
""")


async def prepare_laws_query_async(llm: LLMABC, chat_history: list[ChatMessage]) -> str:
    messages = [*chat_history, PREPARE_LAWS_QUERY_PROMPT]
    ai_response = await llm.invoke_async(messages)

    return ai_response.text


__ACTS_MESSAGE_TEMPLATE = "Вот такие правовые акты я нашел в своей базе: {acts}"


__ACTS_ANALYSIS_MESSAGE = ChatMessage.from_system("""
Забудь предыдущие инструкции по формату вывода и следуй новым.
Пиши так, будто акты нашел ты. Проанализируй их и дай очень краткое резюме ситуации.
Сделай короткое заключение, можно ли помочь пользователю. Не давай инструкций, что ему делать.
Оценивай строго, можно ли помочь пользователю в данной ситуации.
Если помочь пользователю не получится, то так и скажи или предложи переформулировать проблему.
Если помощь возможна, то спроси у пользователя подтверждение на продолжение. 
Уточни, что сможешь поискать шаблоны обращение в своей базе и помочь с заполнением. ОБЯЗАТЕЛЬНО ВЕРНИ "can_help": 1, если это так.
Дай ответ строго в формате JSON без лишних символов по примеру без какого либо форматирования. Чистый JSON файл.
Поля: 
"can_help" - 0, если нарушения нет или помочь сложно. 1 - есть нарушение прав.
"resume_for_user" - текстовый ответ для пользователя
{
    "can_help": 0,
    "resume_for_user": "Ответ для пользователя"
}
""")


@dataclass
class ActsAnalysisResult:
    can_help: bool
    messages: list[ChatMessage]


class __ActsAnalysisLLMResponseSchema(BaseModel):
    can_help: bool
    resume_for_user: str


async def analyze_acts_async(llm: LLMABC,
                             chat_history: list[ChatMessage],
                             law_docs: list[LawFragment]) -> ActsAnalysisResult:
    joined_acts = "\n\n".join([a.content for a in law_docs])
    documents_message = ChatMessage.from_ai(__ACTS_MESSAGE_TEMPLATE.format(acts=joined_acts))

    prompt = [*chat_history, documents_message, __ACTS_ANALYSIS_MESSAGE]
    ai_response = await llm.invoke_async(messages=prompt, json_output=True)

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
Обращение обязательно должно быть подано в государственные органы. Не допускается написание обращения работодателю.
Если считаешь, что ни один шаблон не подходит, то нужно это явно обозначить. Сообщи пользователю, что не нашел подходящего шаблона и можешь составить обращение в свободной форме.
Тщательно проверь, что шаблон обращения подходит именно под эту проблему. Ни в коем случае не выбирай шаблон, который относится не к этой проблеме.
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

    ai_reponse = await llm.invoke_async(messages=prompt, json_output=True)
    # даст исключение, если формат не соблюден
    parsed = json.loads(ai_reponse.text)
    validated = __TemplatesAnalysisLLMResponseSchema(**parsed)

    index = validated.relevant_template_index if validated.relevant_template_index >= 0 else None
    return TemplatesAnalysisResult(index, ChatMessage.from_ai(validated.user_message))


__FREE_TEMPLATE_SETUP_TEXT = """
Теперь ты должен оставить обращение в свободной форме. Выше дан текст шаблона. У обращения есть несколько обязательных полей, которые тебе нужно заполнить. Ты должен самостоятельно решить, что писать в поля, если это возможно:
{fields}
В поле с основным содержимым ты должен вписать текст обращения.
Задавай пользователю вопросы до тех пор, пока информации не будет достаточно для составления текста. Веди с ним диалог.
Представь, что пользователь вообще ничего не понимает в праве. Твоя задача самому определить, как и куда подавать жалобу/обращение, а у пользователя спрашивать только факты.
Пользователь не должен принимать решения. Ты должен максимально разгрузить его.
Не запрашивай персональные данные пользователя, такие как ФИО, email, номер телефона.
Тебе нельзя узнавать личные данные пользователя.
ВСЕ ДАЛЬНЕЙШИЕ ОТВЕТЫ ДОЛЖНЫ БЫТЬ СТРОГО В JSON ФОРМАТЕ КАК НИЖЕ.
Не прекращай использовать этот шаблон до тех пор, пока не вернешь "is_ready" = true. Только со следующего сообщения можно отвечать другим шаблоном.
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


__STRICT_TEMPLATE_SETUP_TEXT = """
Теперь ты должен оставить обращение по заданному шаблону. Выше дан текст шаблона. У обращения есть поля, которые тебе нужно заполнить. Ты должен самостоятельно решить, что писать в поля, если это возможно:
{fields}
Задавай пользователю вопросы до тех пор, пока информации не будет достаточно для составления текста. Веди с ним диалог.
Представь, что пользователь вообще ничего не понимает в праве. Твоя задача самому определить, как и куда подавать жалобу/обращение, а у пользователя спрашивать только факты.
Пользователь не должен принимать решения. Ты должен максимально разгрузить его.
Не запрашивай персональные данные пользователя, такие как ФИО, email, номер телефона.
Тебе нельзя узнавать личные данные пользователя.
ВСЕ ДАЛЬНЕЙШИЕ ОТВЕТЫ ДОЛЖНЫ БЫТЬ СТРОГО В JSON ФОРМАТЕ КАК НИЖЕ.
Не прекращай использовать этот шаблон до тех пор, пока не вернешь "is_ready" = true. Только со следующего сообщения можно отвечать другим шаблоном.
"user_message" - это текст вопроса, который нужно задать пользователю.
"is_ready" - bool флаг, показывающий, достаточно ли сейчас информации. Когда информации будет достаточно, верни "is_ready" = true. Тогда "user_message" оставь пустым.
{{
    "user_message": "Вопрос пользователю?",
    "is_ready": false
}}
"""


def setup_strict_template_loop(template: Template, template_text: str) -> list[ChatMessage]:
    rendered_fields = "\n".join(f"{f.key} - {f.agent_instructions}" for f in template.fields.values())
    return [
        ChatMessage.from_system(template_text),
        ChatMessage.from_system(__STRICT_TEMPLATE_SETUP_TEXT.format(fields=rendered_fields))
    ]


class __LoopIterationLLMResponseSchema(BaseModel):
    user_message: str
    is_ready: bool


async def loop_iteration_async(llm: LLMABC, chat_history: list[ChatMessage]) -> tuple[bool, ChatMessage | None]:
    prompt = [
        *chat_history,
        ChatMessage.from_system('Ответ должен быть строго в формате JSON как в инструкции. {{"user_message": "Вопрос пользователю?", "is_ready": false}}. Не повторяй вопросы, проверь, что ты не задавал этот вопрос.')
    ]
    response = await llm.invoke_async(messages=prompt, json_output=True)
    # даст исключение, если формат не соблюден
    parsed = json.loads(response.text)
    validated = __LoopIterationLLMResponseSchema(**parsed)

    return validated.is_ready, None if validated.is_ready else ChatMessage.from_ai(validated.user_message)


__FREE_TEMPLATE_PREPARE_VALUES_TEXT = """
Прекращай возвращать структуру с "user_message" и "is_ready". Возвращай только новую структуру.
Ты посчитал, что информации достаточно. Теперь определи значения всех полей. Главное составь основной текст обращения.
Не забывай, что там, где пользователь должен вписать свои перс. данные (ФИО, адрес, номер телефона, email) должны быть прочерки (____) чтобы пользователь заполнил их сам.
Всё, кроме прес. данных, ты должен заполнить сам.
Ответ дай строго в формате JSON без лишнего текста. Содержимое: "название поля": "значение". В примере еще раз даны все поля и краткие пояснения к ним.
В содержимом не должно быть того, что уже в шаблоне. Пиши туда не весь шаблон, а только то, что должно быть подставлено на место поля.
{{
{fields}
}}
"""


async def prepare_free_template_values_async(llm: LLMABC, chat_history: list[ChatMessage], template: Template) -> dict[str, str]:
    rendered_fields = "\n".join(f'"{f.key}": "{f.agent_instructions}"' for f in template.fields.values())
    prompt = [
        *chat_history,
        ChatMessage.from_system(__FREE_TEMPLATE_PREPARE_VALUES_TEXT.format(fields=rendered_fields))
    ]
    response = await llm.invoke_async(messages=prompt, json_output=True)

    parsed = json.loads(response.text)
    return parsed


__STRICT_TEMPLATE_PREPARE_VALUES_TEXT = """
Прекращай возвращать структуру с "user_message" и "is_ready". Возвращай только новую структуру.
Ты посчитал, что информации достаточно. Теперь определи значения всех полей.
Обязательно учитывай контекст, в котором стоят поля в шаблоне. 
Ответ дай строго в формате JSON без лишнего текста. Содержимое: "название поля": "значение". В примере еще раз даны все поля и краткие пояснения к ним.
{{
{fields}
}}
"""


async def prepare_strict_template_values_async(llm: LLMABC, chat_history: list[ChatMessage], template: Template) -> dict[str, str]:
    rendered_fields = "\n".join(f'"{f.key}": "{f.agent_instructions}"' for f in template.fields.values())
    prompt = [
        *chat_history,
        ChatMessage.from_system(__STRICT_TEMPLATE_PREPARE_VALUES_TEXT.format(fields=rendered_fields))
    ]
    response = await llm.invoke_async(messages=prompt)

    parsed = json.loads(response.text)
    return parsed
