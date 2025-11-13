from langgraph.graph import StateGraph, START, END
import logging

from src.core.chat_graph.common import BaseState, InputState, create_process_confirmation_node
from src.dto.messages import ChatMessage
from src.core import llm_use_cases
from src.core.laws import LawDocsRepositoryABC
from src.core.llm import LLMABC
from src.application.provider import inject_global


class LawsAnalysisSubgraph(StateGraph[BaseState, None, InputState, BaseState]):

    __logger: logging.Logger

    def __init__(self):
        super().__init__(BaseState, input_schema=InputState)    # type: ignore
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__build()

    def __build(self):
        self.add_edge(START, "save_first_info")
        self.add_node("save_first_info", self.__save_first_info)
        self.add_edge("save_first_info", "find_law_documents")

        self.add_node("find_law_documents", self.__find_law_documents)
        self.add_edge("find_law_documents", "analyze_first_info")

        self.add_node("analyze_first_info", self.__analyze_first_info)
        self.add_conditional_edges("analyze_first_info", self.__continue_if_true("can_help"), {
            "continue": "confirm0",
            "END": END
        })

        self.add_node("confirm0", create_process_confirmation_node("laws_confirmed", self.__logger))

    async def __save_first_info(self, state: InputState) -> BaseState:
        system_message = llm_use_cases.get_start_system_message()
        first_user_message = ChatMessage.from_user(state["first_description"])

        self.__logger.info(f"Saving first message: {state["first_description"]}")
        return {"messages": [system_message, first_user_message]}

    @inject_global
    async def __find_law_documents(self, state: BaseState, repo: LawDocsRepositoryABC) -> BaseState:
        docs = await repo.find_fragments_async(state["messages"][0].text)

        self.__logger.info(f"Adding documents: \n{docs}")
        return {"law_docs": docs}

    @inject_global
    async def __analyze_first_info(self, state: BaseState, llm: LLMABC) -> BaseState:
        acts_analysis_result = await llm_use_cases.analyze_acts_async(llm, state["messages"], state["law_docs"])
        self.__logger.info(f"Acts analysis result: {acts_analysis_result}")
        return {"can_help": acts_analysis_result.can_help, "messages": acts_analysis_result.messages}

    def __continue_if_true(self, key: str):
        def wrapper(state: BaseState):
            self.__logger.info(f"Edge check true ({key}): {state[key]}")
            if not state[key]:
                return "END"

            return "continue"

        return wrapper
