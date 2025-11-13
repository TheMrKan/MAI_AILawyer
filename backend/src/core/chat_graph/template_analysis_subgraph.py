from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
import logging
import asyncio

from src.core.chat_graph.states import BaseState
from src.core.chat_graph.common import create_process_confirmation_node
from src.dto.messages import ChatMessage


class TemplateAnalysisSubgraph(StateGraph[BaseState, None, BaseState, BaseState]):

    __logger: logging.Logger

    def __init__(self):
        super().__init__(BaseState)    # type: ignore
        self.__logger = logging.getLogger(self.__class__.__name__)

        self.__build()

    def __build(self):
        self.add_edge(START, "find_templates")
        self.add_node("find_templates", self.__find_templates)
        self.add_edge("find_templates", "analyze_templates")
        self.add_node("analyze_templates", self.__analyze_templates)
        self.add_conditional_edges("analyze_templates", lambda state: bool(state["relevant_template"]), {
            True: "confirm1",
            False: END
        })

        self.add_node("confirm1", create_process_confirmation_node("template_confirmed", self.__logger))

    async def __find_templates(self, state: BaseState) -> BaseState:
        self.__logger.info("Searching for templates...")
        await asyncio.sleep(1)
        templates = ["Шаблон 1 (strict)", "Шаблон 2 (free)", "Шаблон 3 (free)", "Шаблон 4 (strict)", "Шаблон 5 (free)"]
        self.__logger.info(f"Found templates: {templates}")
        return {"templates": templates}

    async def __analyze_templates(self, state: BaseState) -> BaseState:
        self.__logger.info("Analyzing templates...")
        await asyncio.sleep(1)
        relevant = state["templates"][1]
        new_messages = [
            ChatMessage.from_ai(f"Нашел подходящий шаблон обращения: {relevant}.\n\n"
                                f"Этот документ бла-бла-бла...\n"
                                f"Хотите, я помогу составить обращение?")
        ]
        self.__logger.info("Selected relevant template: %s", relevant)
        return {"relevant_template": relevant, "messages": new_messages}
