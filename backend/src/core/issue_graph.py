from typing import TypedDict, Annotated
import logging
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
from langgraph.runtime import Runtime

from src.core import llm_use_cases
from src.core.laws import LawDocsRepositoryABC
from src.core.llm import LLMABC
from src.dto.laws import LawFragment
from src.dto.messages import ChatMessage
from src.application.provider import Provider


logger = logging.getLogger(__name__)


class InputState(TypedDict):
    first_description: str


def _add_messages_to_state(left: list[ChatMessage], right: list[ChatMessage] | ChatMessage) -> list[ChatMessage]:
    if isinstance(right, ChatMessage):
        return left + [right]

    return left + right


class State(TypedDict):
    # Annotated и add_messages обеспечивает добавление новых сообщений в конец списка, вместо перезаписи всего списка
    messages: Annotated[list[ChatMessage], _add_messages_to_state]
    law_docs: list[LawFragment]
    can_help: bool
    confirmation_0: bool


class RuntimeContext:
    provider: Provider

    def __getitem__[IFACE](self, item: type[IFACE]) -> IFACE:
        return self.provider[item]


class IssueGraph(StateGraph[State, RuntimeContext, InputState]):

    def __init__(self):
        super().__init__(State, RuntimeContext, input_schema=InputState)    # type: ignore
        self.__build()

    def __build(self):
        self.add_node("save_first_info", self.__save_first_info)
        self.add_node("find_law_documents", self.__find_law_documents)
        self.add_node("analyze_first_info", self.__analyze_first_info)
        self.add_node("request_confirmation_0", self.__request_confirmation_0)
        self.add_node("tmp_continue", self.__tmp_continue)

        self.add_edge(START, "save_first_info")
        self.add_edge("save_first_info", "find_law_documents")
        self.add_edge("find_law_documents", "analyze_first_info")
        self.add_conditional_edges("analyze_first_info", self.__continue_if_true("can_help"), {
            "continue": "request_confirmation_0",
            "END": END
        })
        self.add_conditional_edges("request_confirmation_0", self.__continue_if_true("confirmation_0"), {
            "continue": "tmp_continue",
            "END": END
        })

    @staticmethod
    async def __save_first_info(state: InputState):
        system_message = llm_use_cases.get_start_system_message()
        first_user_message = ChatMessage.from_user(state["first_description"])

        logger.info(f"Saving first message: {state["first_description"]}")
        return {"messages": [system_message, first_user_message]}

    @staticmethod
    async def __find_law_documents(state: State, runtime: Runtime[RuntimeContext]):
        docs = await runtime.context[LawDocsRepositoryABC].find_fragments_async(state["messages"][0].text)

        logger.info(f"Adding documents: \n{docs}")
        return {"law_docs": docs}

    @staticmethod
    async def __analyze_first_info(state: State, runtime: Runtime[RuntimeContext]):
        llm = runtime.context[LLMABC]
        acts_analysis_result = await llm_use_cases.analyze_acts_async(llm, state["messages"], state["law_docs"])
        logger.info(f"Acts analysis result: {acts_analysis_result}")
        return {"can_help": acts_analysis_result.can_help, "messages": acts_analysis_result.messages}

    @staticmethod
    def __continue_if_true(key: str):
        def wrapper(state: State):
            logger.info(f"Edge check true ({key}): {state[key]}")
            if not state[key]:
                return "END"

            return "continue"
        return wrapper

    @staticmethod
    async def __request_confirmation_0(state: State, runtime: Runtime[RuntimeContext]):
        user_input = interrupt(None)
        user_message = ChatMessage.from_user(user_input)
        is_confirmed = await llm_use_cases.is_agreement_async(runtime.context[LLMABC], user_message)
        logger.info(f"Got user confirmation input ({is_confirmed}): {user_input}")
        return {"confirmation_0": is_confirmed, "messages": ChatMessage.from_user(user_input)}

    @staticmethod
    async def __tmp_continue(state: State):
        logger.info("CONTINUE")

