from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
import logging

from src.core.chat_graph.common import BaseState, FreeTemplateState
from src.core.templates.service import TemplateService
from src.core.templates.file_service import TemplateFileService
from src.core import llm_use_cases
from src.core.llm import LLMABC
from src.dto.messages import ChatMessage
from src.application.provider import inject_global


class FreeTemplateSubgraph(StateGraph[FreeTemplateState, None, BaseState, FreeTemplateState]):

    __logger: logging.Logger

    def __init__(self):
        super().__init__(BaseState)    # type: ignore
        self.__logger = logging.getLogger(self.__class__.__name__)

        self.__build()

    def __build(self):
        self.add_edge(START, "setup_loop")
        self.add_node("setup_loop", self.__setup_loop)
        self.add_edge("setup_loop", "ask")

        self.add_node("ask", self.__ask)
        self.add_edge("ask", "handle_answer"),
        self.add_node("handle_answer", self.__handle_answer)
        self.add_conditional_edges("handle_answer", lambda state: state.get("loop_completed", False), {
            False: "ask",
            True: END
        })

    @inject_global
    async def __setup_loop(self,
                           state: BaseState,
                           service: TemplateService,
                           file_service: TemplateFileService) -> FreeTemplateState:
        self.__logger.debug("Setting up QA loop...")

        free_template = await service.get_free_template_async()
        text = file_service.extract_text(free_template)

        return {"messages": llm_use_cases.setup_free_template_loop(free_template, text)}

    def __ask(self, state: FreeTemplateState) -> FreeTemplateState:
        self.__logger.debug("Asking...")
        return {"messages": [
            ChatMessage.from_system("Задай дополнительный вопрос"),
            ChatMessage.from_ai("Уточняющий вопрос?"),
        ]}

    def __handle_answer(self, state: FreeTemplateState) -> FreeTemplateState:
        user_input = interrupt(None)
        user_message = ChatMessage.from_user(user_input)
        self.__logger.debug("Got user answer: %s", user_input)

        new_messages = [user_message]

        # проверка на достаточность информации
        if "достаточно" in user_input.lower():
            return {"messages": new_messages, "loop_completed": True}

        return {"messages": new_messages}
