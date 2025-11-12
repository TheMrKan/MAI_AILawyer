from langgraph.checkpoint.memory import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command, StateSnapshot

from src.core.chat_graph.full_chat_graph import FullChatGraph, InputState
from src.dto.messages import ChatMessage


class GraphError(Exception):
    pass


class GraphController:

    checkpointer: BaseCheckpointSaver
    graph: CompiledStateGraph

    def __init__(self,  checkpointer: BaseCheckpointSaver):
        self.checkpointer = checkpointer

        self.graph = self.__compile_graph(checkpointer)

    @staticmethod
    def __compile_graph(checkpointer: BaseCheckpointSaver) -> CompiledStateGraph:
        graph = FullChatGraph()
        compiled = graph.compile(checkpointer=checkpointer)
        return compiled

    async def invoke_with_new_message(self, thread_id: int, message_text: str) -> list[ChatMessage]:
        graph_config = {"configurable": {"thread_id": thread_id}}
        graph_state = await self.graph.aget_state(graph_config)

        skip_messages = 0

        if not self.__is_exists(graph_state):
            graph_input = InputState(first_description=message_text)
        elif self.__is_ended(graph_state):
            raise GraphError("Чат завершен")
        else:
            graph_input = Command(resume=message_text)
            history = graph_state.values.get("messages", [])
            skip_messages = len(history)

        result = await self.graph.ainvoke(graph_input, graph_config)
        return result["messages"][skip_messages:]

    async def is_ended(self, thread_id: int) -> bool:
        graph_config = {"configurable": {"thread_id": thread_id}}
        graph_state = await self.graph.aget_state(graph_config)
        return self.__is_ended(graph_state)

    @staticmethod
    def __is_exists(graph_state: StateSnapshot) -> bool:
        return graph_state.created_at is not None

    @staticmethod
    def __is_ended(graph_state: StateSnapshot) -> bool:
        return not any(graph_state.next)