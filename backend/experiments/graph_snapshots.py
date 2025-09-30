import json

from fastapi import FastAPI
from pydantic import BaseModel
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver


class State(TypedDict):
    user_input: str
    message_history: list[str]
    acts: list[str]
    is_user_agreed: bool



def process_first_info(state: State):
    return {"user_input": "", "message_history": [state["user_input"]]}


def find_acts(state: State):
    return {"acts": ["Закон 1234", "Закон 456"]}


def analyze(state: State):
    return {"message_history": state["message_history"] + [f"Вот такие я нашел: {state['acts']}. Всё нормально. Вас устраивает?"]}


def process_response(state: State):
    response = interrupt("Продолжаем? ")
    if response == "YES":
        return {"is_user_agreed": True}
    elif response == "NO":
        return {"is_user_agreed": False}
    else:
        return {}


def is_input_ready(state: State):
    if "is_user_agreed" not in state:
        return "retry"

    if state["is_user_agreed"]:
        return "cont"
    else:
        return "break"


def cont(state: State):
    print("Продолжаем работу...")
    return {}


workflow = StateGraph(State)


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

thread = {"configurable": {"thread_id": "1"}}

command = {"user_input": "Моя проблема"}

while True:

    question = None
    for event in graph.stream(command, thread, stream_mode="updates"):
        if "__interrupt__" not in event:
            print(event)
            continue

        question = event["__interrupt__"][0].value

    print(graph.get_state(thread).interrupts)    # Если список не пустой, то диалог был прерван, т. е. возобновляем с resume

    if not question:
        print("No question found")
        break

    response = input(question)
    question = None
    command = Command(resume=response)
