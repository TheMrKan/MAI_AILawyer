from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
import logging

from src.core.chat_graph.common import BaseState, StrictTemplateState
from src.dto.messages import ChatMessage


class StrictTemplateSubgraph(StateGraph[StrictTemplateState, None, BaseState, StrictTemplateState]):

    __logger: logging.Logger

    def __init__(self):
        super().__init__(StrictTemplateState)    # type: ignore
        self.__logger = logging.getLogger(self.__class__.__name__)

        self.__build()

    def __build(self):
        self.add_edge(START, "setup_loop")
        self.add_node("setup_loop", self.__setup_loop)
        self.add_edge("setup_loop", "ask")

        self.add_node("ask", self.__ask)
        self.add_edge("ask", "process_answer")
        self.add_node("process_answer", self.__process_answer)
        self.add_conditional_edges("process_answer", lambda state: state.get("loop_completed", False), {
            False: "ask",
            True: END
        })

    def __setup_loop(self, state: BaseState) -> StrictTemplateState:
        self.__logger.debug("Setting up strict QA loop")
        new_messages = [
            ChatMessage.from_system("Инструкции и т. д.")
        ]

        return {"messages": new_messages}

    def __ask(self, state: StrictTemplateState) -> StrictTemplateState:
        new_messages = [
            ChatMessage.from_system("Задай уточняющий вопрос"),
            ChatMessage.from_ai("Какое значение этого поля?")
        ]

        return {"messages": state["messages"] + new_messages}

    def __process_answer(self, state: StrictTemplateState) -> StrictTemplateState:
        user_input = interrupt(None)
        user_message = ChatMessage.from_user(user_input)

        fields = state.setdefault("fields", {})
        tmp_value = len(tuple(m for m in state["messages"] if m.role == m.role.AI))
        fields[str(tmp_value)] = user_input

        if "достаточно" in user_message.text.lower():
            self.__logger.debug("Completing loop with fields %s", fields)
            return {"messages": [*state["messages"], user_message], "fields": fields, "loop_completed": True}

        return {"messages": [*state["messages"], user_message], "fields": fields}
