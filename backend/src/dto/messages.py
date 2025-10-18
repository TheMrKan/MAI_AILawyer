from dataclasses import dataclass
from enum import Enum
from typing import Self


class MessageRole(Enum):
    SYSTEM = "system"
    USER = "user"
    AI = "ai"


@dataclass(frozen=True)    # frozen, чтобы избежать непреднамеренных изменений
class ChatMessage:
    text: str
    role: MessageRole

    # отказался от названий system, user, ai, чтобы не вводили в заблуждение
    # например, message.user выглядит как отправитель сообщения
    @classmethod
    def from_system(cls, text: str) -> Self:
        return cls(text=text, role=MessageRole.SYSTEM)

    @classmethod
    def from_user(cls, text: str) -> Self:
        return cls(text=text, role=MessageRole.USER)

    @classmethod
    def from_ai(cls, text: str) -> Self:
        return cls(text=text, role=MessageRole.AI)



