from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
import logging

from src.core.chats.graph.common import BaseState, InputState, create_process_confirmation_node
from src.core.chats.types import ChatMessage
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
        self.add_edge("save_first_info", "analyze_info")

        self.add_node("analyze_info", self.__analyze_info)
        self.add_conditional_edges("analyze_info", lambda state: state.get("first_info_completed", False), {
            True: "find_law_documents",
            False: "handle_answer"
        })

        self.add_node("handle_answer", self.__handle_answer)
        self.add_edge("handle_answer", "analyze_info")

        self.add_node("find_law_documents", self.__find_law_documents)
        self.add_edge("find_law_documents", "analyze_law_documents")

        self.add_node("analyze_law_documents", self.__analyze_law_documents)
        self.add_conditional_edges("analyze_law_documents", self.__continue_if_true("can_help"), {
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
    async def __analyze_info(self, state: BaseState, llm: LLMABC) -> BaseState:
        self.__logger.info(f"Analyzing given info...")

        result = await llm_use_cases.analyze_first_info_async(llm, state["messages"])
        if result.is_ready_to_continue:
            return {"first_info_completed": True}

        return {"messages": [*state["messages"], ChatMessage.from_ai(result.user_message)]}

    def __handle_answer(self, state: BaseState):
        user_input = interrupt(None)
        user_message = ChatMessage.from_user(user_input)
        self.__logger.debug("Got user answer: %s", user_input)

        return {"messages": [*state["messages"], user_message]}

    @inject_global
    async def __find_law_documents(self, state: BaseState, llm: LLMABC, repo: LawDocsRepositoryABC) -> BaseState:
        query = await llm_use_cases.prepare_laws_query_async(llm, state["messages"])
        self.__logger.debug("Prepared laws query: %s", query)

        docs = await repo.find_fragments_async(query)

        self.__logger.info(f"Adding documents: \n{docs}")
        return {"law_docs": docs}

    @inject_global
    async def __analyze_law_documents(self, state: BaseState, llm: LLMABC) -> BaseState:
        acts_analysis_result = await llm_use_cases.analyze_acts_async(llm, state["messages"], state["law_docs"])
        self.__logger.info(f"Acts analysis result: {acts_analysis_result}")
        return {"can_help": acts_analysis_result.can_help, "messages": state["messages"] + acts_analysis_result.messages}

    def __continue_if_true(self, key: str):
        def wrapper(state: BaseState):
            self.__logger.info(f"Edge check true ({key}): {state[key]}")
            if not state[key]:
                return "END"

            return "continue"

        return wrapper
