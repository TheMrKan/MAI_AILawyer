from langgraph.types import interrupt
import logging

from src.application.provider import inject_global
from src.core import llm_use_cases
from src.core.chat_graph.states import BaseState
from src.core.llm import LLMABC
from src.dto.messages import ChatMessage


def create_process_confirmation_node(write_to: str, logger: logging.Logger):
    @inject_global
    async def _internal(state: BaseState, llm: LLMABC) -> BaseState:
        user_input = interrupt(None)
        user_message = ChatMessage.from_user(user_input)
        is_confirmed = await llm_use_cases.is_agreement_async(llm, user_message)
        logger.info(f"Got user confirmation input (for {write_to}) ({is_confirmed}): {user_input}")
        return {write_to: is_confirmed, "messages": [ChatMessage.from_user(user_input)]}

    return _internal