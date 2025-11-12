from typing import TypedDict, Annotated
import logging
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
import asyncio

from src.core import llm_use_cases
from src.core.laws import LawDocsRepositoryABC
from src.core.llm import LLMABC
from src.dto.laws import LawFragment
from src.dto.messages import ChatMessage
from src.application.provider import inject_global


logger = logging.getLogger(__name__)


class InputState(TypedDict):
    first_description: str


def _add_messages_to_state(left: list[ChatMessage], right: list[ChatMessage] | ChatMessage) -> list[ChatMessage]:
    if isinstance(right, ChatMessage):
        return left + [right]

    return left + right


class State(TypedDict, total=False):
    # Annotated и add_messages обеспечивает добавление новых сообщений в конец списка, вместо перезаписи всего списка
    messages: Annotated[list[ChatMessage], _add_messages_to_state]
    law_docs: list[LawFragment]
    can_help: bool
    confirmation_0: bool
    templates: list[str]
    relevant_template: str | None


class IssueGraph(StateGraph[State, None, InputState]):

    def __init__(self):
        super().__init__(State, input_schema=InputState)    # type: ignore
        self.__build()

    def __build(self):
        self.add_node("save_first_info", self.__save_first_info)
        self.add_node("find_law_documents", self.__find_law_documents)
        self.add_node("analyze_first_info", self.__analyze_first_info)
        self.add_node("request_confirmation_0", self.__request_confirmation_0)
        self.add_node("find_templates", self.__find_templates)
        self.add_node("analyze_templates", self.__analyze_templates)

        self.add_edge(START, "save_first_info")
        self.add_edge("save_first_info", "find_law_documents")
        self.add_edge("find_law_documents", "analyze_first_info")
        self.add_conditional_edges("analyze_first_info", self.__continue_if_true("can_help"), {
            "continue": "request_confirmation_0",
            "END": END
        })
        self.add_conditional_edges("request_confirmation_0", self.__continue_if_true("confirmation_0"), {
            "continue": "find_templates",
            "END": END
        })
        self.add_edge("find_templates", "analyze_templates")



    @staticmethod
    async def __save_first_info(state: InputState) -> State:
        system_message = llm_use_cases.get_start_system_message()
        first_user_message = ChatMessage.from_user(state["first_description"])

        logger.info(f"Saving first message: {state["first_description"]}")
        return {"messages": [system_message, first_user_message]}

    @staticmethod
    @inject_global
    async def __find_law_documents(state: State, repo: LawDocsRepositoryABC) -> State:
        docs = await repo.find_fragments_async(state["messages"][0].text)

        logger.info(f"Adding documents: \n{docs}")
        return {"law_docs": docs}

    @staticmethod
    @inject_global
    async def __analyze_first_info(state: State, llm: LLMABC) -> State:
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
    @inject_global
    async def __request_confirmation_0(state: State, llm: LLMABC) -> State:
        user_input = interrupt(None)
        user_message = ChatMessage.from_user(user_input)
        is_confirmed = await llm_use_cases.is_agreement_async(llm, user_message)
        logger.info(f"Got user confirmation input ({is_confirmed}): {user_input}")
        return {"confirmation_0": is_confirmed, "messages": [ChatMessage.from_user(user_input)]}

    @staticmethod
    async def __find_templates(state: State) -> State:
        logger.info("Searching for templates...")
        await asyncio.sleep(1)
        templates = ["Шаблон 1", "Шаблон 2", "Шаблон 3", "Шаблон 4", "Шаблон 5"]
        logger.info(f"Found templates: {templates}")
        return {"templates": templates}

    @staticmethod
    async def __analyze_templates(state: State) -> State:
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



