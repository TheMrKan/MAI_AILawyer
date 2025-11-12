from typing import TypedDict, Annotated

from src.dto.laws import LawFragment
from src.dto.messages import ChatMessage


def _add_messages_to_state(left: list[ChatMessage], right: list[ChatMessage] | ChatMessage) -> list[ChatMessage]:
    if isinstance(right, ChatMessage):
        return left + [right]

    return left + right


class BaseState(TypedDict, total=False):
    # Annotated и add_messages обеспечивает добавление новых сообщений в конец списка, вместо перезаписи всего списка
    messages: Annotated[list[ChatMessage], _add_messages_to_state]
    law_docs: list[LawFragment]
    can_help: bool
    confirmation_0: bool
    templates: list[str]
    relevant_template: str | None
    confirmation_1: bool