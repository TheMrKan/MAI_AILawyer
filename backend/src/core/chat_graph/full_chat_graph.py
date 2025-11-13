from typing import TypedDict
import logging
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
import asyncio

from src.core.chat_graph.states import BaseState, InputState
from src.core.chat_graph.laws_analysis_subgraph import LawsAnalysisSubgraph
from src.core import llm_use_cases
from src.core.laws import LawDocsRepositoryABC
from src.core.llm import LLMABC
from src.dto.messages import ChatMessage
from src.application.provider import inject_global


logger = logging.getLogger(__name__)


class FullChatGraph(StateGraph[BaseState, None, InputState]):

    def __init__(self):
        super().__init__(BaseState, input_schema=InputState)    # type: ignore
        self.__build()

    def __build(self):
        self.add_edge(START, "laws_analysis_subgraph")
        self.add_node("laws_analysis_subgraph", LawsAnalysisSubgraph().compile())
        self.add_conditional_edges("laws_analysis_subgraph", self.__continue_if_true("confirmation_0"), {
            "continue": "find_templates",
            "END": END
        })

        self.add_node("find_templates", self.__find_templates)
        self.add_edge("find_templates", "analyze_templates")
        self.add_node("analyze_templates", self.__analyze_templates)
        self.add_conditional_edges("analyze_templates", self.__continue_if_true("relevant_template"), {
            "continue": "confirm1",
            "END": END
        })

        self.add_node("confirm1", self.__process_confirmation("confirmation_1"))

        self.add_conditional_edges("confirm1", self.__path_selector, {
            "free": END,
            "strict": END,
        })

    @staticmethod
    async def __find_templates(state: BaseState) -> BaseState:
        logger.info("Searching for templates...")
        await asyncio.sleep(1)
        templates = ["Шаблон 1 (strict)", "Шаблон 2 (free)", "Шаблон 3 (free)", "Шаблон 4 (strict)", "Шаблон 5 (free)"]
        logger.info(f"Found templates: {templates}")
        return {"templates": templates}

    @staticmethod
    async def __analyze_templates(state: BaseState) -> BaseState:
        logger.info("Analyzing templates...")
        await asyncio.sleep(1)
        relevant = state["templates"][1]
        new_messages = [
            ChatMessage.from_ai(f"Нашел подходящий шаблон обращения: {relevant}.\n\n"
                                f"Этот документ бла-бла-бла...\n"
                                f"Хотите, я помогу составить обращение?")
        ]
        logger.info("Selected relevant template: %s", relevant)
        return {"relevant_template": relevant, "messages": new_messages}

    @staticmethod
    def __path_selector(state: BaseState) -> str:
        if not state["confirmation_1"]:
            return "END"

        if "free" in state["relevant_template"]:
            return "free"
        return "strict"

    @staticmethod
    def __continue_if_true(key: str):
        def wrapper(state: BaseState):
            logger.info(f"Edge check true ({key}): {state[key]}")
            if not state[key]:
                return "END"

            return "continue"

        return wrapper

    @staticmethod
    def __process_confirmation(write_to: str):
        @inject_global
        async def _internal(state: BaseState, llm: LLMABC) -> BaseState:
            user_input = interrupt(None)
            user_message = ChatMessage.from_user(user_input)
            is_confirmed = await llm_use_cases.is_agreement_async(llm, user_message)
            logger.info(f"Got user confirmation input (for {write_to}) ({is_confirmed}): {user_input}")
            return {write_to: is_confirmed, "messages": [ChatMessage.from_user(user_input)]}

        return _internal



