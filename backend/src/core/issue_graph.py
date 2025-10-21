from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt

from src.core.container import Container
from src.core.llm_use_cases import LLMUseCases
from src.dto.messages import ChatMessage


class InputState(TypedDict):
    first_description: str


def _add_messages_to_state(left: list[ChatMessage], right: list[ChatMessage] | ChatMessage) -> list[ChatMessage]:
    if isinstance(right, ChatMessage):
        return left + [right]

    return left + right


class State(TypedDict):
    # Annotated и add_messages обеспечивает добавление новых сообщений в конец списка, вместо перезаписи всего списка
    messages: Annotated[list[ChatMessage], _add_messages_to_state]
    acts: list[str]
    can_help: bool


class IssueGraph(StateGraph[State, None, InputState]):

    def __init__(self):
        super().__init__(State, input_schema=InputState)    # type: ignore
        self.__build()

    def __build(self):
        self.add_node("save_first_info", self.__save_first_info)
        self.add_node("find_law_documents", self.__find_law_documents)
        self.add_node("analyze_first_info", self.__analyze_first_info)
        self.add_node("request_confirmation_0", self.__request_confirmation_0)

        self.add_edge(START, "save_first_info")
        self.add_edge("save_first_info", "find_law_documents")
        self.add_edge("find_law_documents", "analyze_first_info")
        self.add_conditional_edges("analyze_first_info", self.__continue_if_can_help, {
            "continue": "request_confirmation_0",
            "END": END
        })

    @staticmethod
    async def __save_first_info(state: InputState):
        system_message = LLMUseCases(Container.LLM_instance).get_start_system_message()
        first_user_message = ChatMessage.from_user(state["first_description"])

        return {"messages": [system_message, first_user_message]}

    @staticmethod
    async def __find_law_documents(state: State):
        docs = await Container.laws_repo.find_fragments_async(state["messages"][0].text)
        message = LLMUseCases(Container.LLM_instance).add_acts_to_dialogue(docs)
        return {"messages": message, "acts": docs}

    @staticmethod
    async def __analyze_first_info(state: State):
        acts_analysis_result = await LLMUseCases(Container.LLM_instance).analyze_acts_async(state["messages"])
        return {"can_help": acts_analysis_result.can_help, "messages": ChatMessage.from_ai(acts_analysis_result.resume_for_user)}

    @staticmethod
    async def __continue_if_can_help(state: State):
        if not state["can_help"]:
            return "END"

        return "continue"

    @staticmethod
    async def __request_confirmation_0(state: InputState):
        user_input = interrupt(None)
