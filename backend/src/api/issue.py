from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from enum import Enum

from src.core import issue_graph
from src.core.issue_graph import GraphError

router = APIRouter(prefix="/issue/{issue_id}")


class AddUserMessage(BaseModel):
    text: str


class MessageType(Enum):
    USER = "user"
    BOT = "bot"


class Message(BaseModel):
    id: int
    message: str
    type: MessageType


class ChatHistoryFragment(BaseModel):
    new_messages: list[Message]


@router.post('/chat/')
async def chat(issue_id: int, message: AddUserMessage) -> ChatHistoryFragment:
    try:
        new_messages = [{"id": 1, "message": t, "type": MessageType.BOT} for t in await issue_graph.invoke_with_new_message(issue_id, message.text)]
    except GraphError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Произошла непредвиденная ошибка")

    return {"new_messages": new_messages}

