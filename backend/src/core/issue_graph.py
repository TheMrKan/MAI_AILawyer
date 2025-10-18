from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.types import interrupt, Command, StateSnapshot
from langgraph.checkpoint.memory import InMemorySaver

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
    is_user_agreed: bool


class GraphError(Exception):
    pass


async def analyze_first_info(state: InputState):
    first_user_message = ChatMessage.from_user(state["first_description"])

    analysis_result = await LLMUseCases(Container.LLM_instance).analyze_first_description_async(first_user_message)

    return {"messages": [first_user_message, analysis_result]}


def find_acts(state: State):
    return {"acts": ["Закон 1234", "Закон 456"]}


async def analyze_acts(state: State):
    acts_analysis_result = await LLMUseCases(Container.LLM_instance).analyze_acts_async(state["messages"], state["acts"])
    return {"messages": [ChatMessage.from_ai(f"Вот такие акты нашлись в моей базе: {state['acts']}"), acts_analysis_result]}


def process_response(state: State):
    new_messages = []
    response = interrupt(None)
    new_messages.append(ChatMessage.from_user(response))

    result = {"messages": new_messages}
    if response == "YES":
        result.update({"is_user_agreed": True})
    elif response == "NO":
        result.update({"is_user_agreed": False})

    return result


def is_input_ready(state: State):
    if "is_user_agreed" not in state:
        return "retry"

    if state["is_user_agreed"]:
        return "cont"
    else:
        return "break"


def cont(state: State):
    return {"messages": [ChatMessage.from_ai("Продолжаем работу...")]}


workflow = StateGraph(State, input_schema=InputState)


workflow.add_node("process_first_info", analyze_first_info)
workflow.add_node("find_acts", find_acts)
workflow.add_node("analyze", analyze_acts)
workflow.add_node("process_response", process_response)
workflow.add_node("cont", cont)

workflow.add_edge(START, "process_first_info")
workflow.add_edge("process_first_info", "find_acts")
workflow.add_edge("find_acts", "analyze")
workflow.add_edge("analyze", "process_response")
workflow.add_conditional_edges("process_response", is_input_ready, {
    "retry": "process_response",
    "cont": "cont",
    "break": END
})
workflow.add_edge("cont", END)

memory = InMemorySaver()

graph = workflow.compile(checkpointer=memory)


async def invoke_with_new_message(thread_id: int, message_text: str) -> list[ChatMessage]:
    graph_config = {"configurable": {"thread_id": thread_id}}
    graph_state = await graph.aget_state(graph_config)

    skip_messages = 0

    if not __is_exists(graph_state):
        graph_input = InputState(first_description=message_text)
    elif __is_ended(graph_state):
        raise GraphError("Чат завершен")
    else:
        graph_input = Command(resume=message_text)
        history = graph_state.values.get("messages", [])
        skip_messages = len(history)

    result = await graph.ainvoke(graph_input, graph_config)
    return result["messages"][skip_messages:]


def __is_exists(graph_state: StateSnapshot) -> bool:
    return graph_state.created_at is not None


def __is_ended(graph_state: StateSnapshot) -> bool:
    return not any(graph_state.next)
