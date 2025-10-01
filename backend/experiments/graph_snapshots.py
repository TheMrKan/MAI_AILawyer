from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver


class InputState(TypedDict):
    first_description: str


class State(TypedDict):
    message_history: list[str]
    acts: list[str]
    is_user_agreed: bool


def process_first_info(state: InputState):
    return {"message_history": [state["first_description"]]}


def find_acts(state: State):
    return {"acts": ["Закон 1234", "Закон 456"]}


def analyze(state: State):
    return {"message_history": state["message_history"] + [f"Вот такие я нашел: {state['acts']}. Всё нормально. Вас устраивает?"]}


def process_response(state: State):
    new_messages = []
    response = interrupt(None)
    new_messages.append(response)

    result = {"message_history": state["message_history"] + new_messages}
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
    return {"message_history": state["message_history"] + ["Продолжаем работу..."]}


workflow = StateGraph(State, input_schema=InputState)


workflow.add_node("process_first_info", process_first_info)
workflow.add_node("find_acts", find_acts)
workflow.add_node("analyze", analyze)
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

app = FastAPI()


class ChatRequest(BaseModel):
    message: str


@app.post("/chat/{chat_id}/")
async def chat_handler(chat_id: int, request: ChatRequest):
    # invoke graph
    graph_config = {"configurable": {"thread_id": chat_id}}
    graph_state = await graph.aget_state(graph_config)

    if graph_state.created_at is None:
        graph_input = InputState(first_description=request.message)
    elif not any(graph_state.next):
        raise HTTPException(status_code=403, detail="Chat ended")
    else:
        graph_input = Command(resume=request.message)

    try:
        result = await graph.ainvoke(graph_input, graph_config)
        response_message = result["message_history"][-1]
    except Exception as e:
        response_message = f"[ERROR] {str(e)}"

    return {"answer": response_message}
