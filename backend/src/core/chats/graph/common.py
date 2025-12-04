from langgraph.types import interrupt
import logging
from typing import TypedDict

from src.application.provider import inject_global
from src.core.llm.iface import LLMABC
from src.core.llm import use_cases as llm_use_cases
from src.core.chats.types import ChatMessage
from src.core.laws.types import LawFragment
from src.core.templates.types import Template


class InputState(TypedDict, total=False):
    """
    Входное состояние графа
    """
    issue_id: int
    first_description: str
    """
    Первое описание проблемы от пользователя. Становится первым сообщением от пользователя в чате.
    """


class BaseState(InputState, total=False):
    """
    Общее состояние для всех подграфов
    """
    messages: list[ChatMessage]
    """
    Полная история сообщений графа.
    """
    first_info_completed: bool
    """
    Завершен цикл начальных вопросов-ответов до поиска правовых актов.
    Определяет LLM на каждой итерации.
    """
    law_docs: list[LawFragment]
    """
    Список найденных правовых актов по данному обращению.
    """
    can_help: bool
    """
    Вердикт LLM, возможно ли помочь в данной ситуации.
    Определяется после анализа найденных правовых актов.
    """
    laws_confirmed: bool
    """
    Пользователь подтвердил работу по найденным правовым актам и вердикту.
    """
    templates: list[Template]
    """
    Список найденных шаблонов по данному обращению.
    """
    relevant_template: Template | None
    """
    Шаблон, который LLM посчитала наиболее подходящим из templates.
    None означает, что ни один шаблон не подходит к ситуации и обращение должно быть составлено в свободной форме.
    """
    template_confirmed: bool
    """
    Пользователь подтвердил работу по выбранному шаблону или в свободной форме.
    """
    field_values: dict[str, str]
    """
    Значения полей в итоговом шаблоне {"field_name": "текст для подстановки в шаблон"}
    """
    success: bool


class FreeTemplateState(BaseState, total=False):
    """
    Доп. поля подграфа свободного обращения
    """
    loop_completed: bool
    """
    Цикл вопросов-ответов для накопления информации завершен. Определяет LLM на каждой итерации.
    """


class StrictTemplateState(BaseState, total=False):
    """
    Доп поля подграфа обращения по шаблону
    """
    loop_completed: bool
    """
    Цикл вопросов-ответов для заполнения полей завершен.
    Определяет LLM на каждой итерации.
    """
    fields: dict[str, str]
    """
    Список полей в шаблоне строгой формы. {"field_id": "инструкции для агента по данному полю"}
    """


def create_process_confirmation_node(write_to: str, logger: logging.Logger):
    """
    Создает функцию-ноду, обрабатывающую "да/нет" подтверждения от пользователя через легкую модель.
    :param write_to: Название поля в состоянии, в которое будет записан True/False результат.
    """
    @inject_global
    async def _internal(state: BaseState, llm: LLMABC) -> BaseState:
        user_input = interrupt(None)
        user_message = ChatMessage.from_user(user_input)
        is_confirmed = await llm_use_cases.is_agreement_async(llm, user_message)
        logger.info(f"Got user confirmation input (for {write_to}) ({is_confirmed}): {user_input}")
        return {write_to: is_confirmed, "messages": [*state["messages"], ChatMessage.from_user(user_input)]}

    return _internal
