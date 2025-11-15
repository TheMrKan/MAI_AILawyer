from langgraph.types import interrupt
import logging
from typing import TypedDict, Annotated

from src.application.provider import inject_global
from src.core import llm_use_cases
from src.core.llm import LLMABC
from src.dto.messages import ChatMessage
from src.dto.laws import LawFragment
from src.core.templates.types import Template


def _add_messages_to_state(left: list[ChatMessage], right: list[ChatMessage] | ChatMessage) -> list[ChatMessage]:
    if isinstance(right, ChatMessage):
        return left + [right]

    return left + right


class InputState(TypedDict, total=False):
    first_description: str


class BaseState(InputState, total=False):
    # Annotated и add_messages обеспечивает добавление новых сообщений в конец списка, вместо перезаписи всего списка
    messages: Annotated[list[ChatMessage], _add_messages_to_state]
    law_docs: list[LawFragment]
    can_help: bool
    laws_confirmed: bool
    templates: list[Template]
    relevant_template: Template | None
    template_confirmed: bool


class FreeTemplateState(BaseState, total=False):
    loop_completed: bool


class StrictTemplateState(BaseState, total=False):
    loop_completed: bool
    fields: dict[str, str]


def create_process_confirmation_node(write_to: str, logger: logging.Logger):
    @inject_global
    async def _internal(state: BaseState, llm: LLMABC) -> BaseState:
        user_input = interrupt(None)
        user_message = ChatMessage.from_user(user_input)
        is_confirmed = await llm_use_cases.is_agreement_async(llm, user_message)
        logger.info(f"Got user confirmation input (for {write_to}) ({is_confirmed}): {user_input}")
        return {write_to: is_confirmed, "messages": [ChatMessage.from_user(user_input)]}

    return _internal