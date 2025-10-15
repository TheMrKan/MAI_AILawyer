from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from enum import Enum
import traceback

from src.core import issue_graph
from src.core.issue_graph import GraphError

router = APIRouter(prefix="/issue/{issue_id}")


class AddUserMessage(BaseModel):
    text: str


class MessageRole(Enum):
    USER = "user"
    BOT = "bot"


class Message(BaseModel):
    message: str
    role: MessageRole


class ChatHistoryFragment(BaseModel):
    new_messages: list[Message]


@router.post('/chat/')
async def chat(issue_id: int, message: AddUserMessage) -> ChatHistoryFragment:
    try:
        messages = await issue_graph.invoke_with_new_message(issue_id, message.text)
        fragment = [{"message": m.text(), "role": MessageRole.BOT.value if issue_graph.is_ai_message(m) else MessageRole.USER.value}
                    for m in messages]
    except GraphError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Произошла непредвиденная ошибка")

    return {"new_messages": fragment}

