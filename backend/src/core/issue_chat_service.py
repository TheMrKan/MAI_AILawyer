from langgraph.checkpoint.memory import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command, StateSnapshot
import logging

from src.core.chat_graph.full_chat_graph import FullChatGraph, InputState
from src.dto.messages import ChatMessage


class GraphError(Exception):
    pass


class IssueChatService:

    checkpointer: BaseCheckpointSaver
    graph: CompiledStateGraph
    __logger: logging.Logger

    def __init__(self,  checkpointer: BaseCheckpointSaver):
        self.checkpointer = checkpointer
        self.__logger = logging.getLogger(self.__class__.__name__)

        self.graph = self.__compile_graph(checkpointer)

    @staticmethod
    def __compile_graph(checkpointer: BaseCheckpointSaver) -> CompiledStateGraph:
        graph = FullChatGraph()
        compiled = graph.compile(checkpointer=checkpointer)
        return compiled

    async def get_messages_async(self, issue_id: int) -> list[ChatMessage]:
        graph_config = {"configurable": {"thread_id": issue_id}}
        graph_state = await self.graph.aget_state(graph_config, subgraphs=True)

        if not self.__is_exists(graph_state):
            raise KeyError("Чат не существует")

        return self.__get_chat_history(graph_state)

    async def process_new_user_message(self, issue_id: int, message_text: str) -> list[ChatMessage]:
        graph_config = {"configurable": {"thread_id": issue_id}}
        graph_state = await self.graph.aget_state(graph_config, subgraphs=True)

        skip_messages = 0

        if not self.__is_exists(graph_state):
            graph_input = InputState(first_description=message_text)
        elif self.__is_ended(graph_state):
            raise GraphError("Чат завершен")
        else:
            graph_input = Command(resume=message_text)
            history = self.__get_chat_history(graph_state)
            skip_messages = len(history)

        result = await self.graph.ainvoke(graph_input, graph_config, subgraphs=True)
        return result["messages"][skip_messages:]

    async def is_ended(self, issue_id: int) -> bool:
        graph_config = {"configurable": {"thread_id": issue_id}}
        graph_state = await self.graph.aget_state(graph_config)
        return self.__is_ended(graph_state)

    @staticmethod
    def __get_chat_history(graph_state: StateSnapshot) -> list[ChatMessage]:
        history = graph_state.values.get("messages", [])
        if any(graph_state.tasks):
            if len(graph_state.tasks[0].state.values.get("messages", [])) > len(history):
                history = graph_state.tasks[0].state.values.get("messages", [])

        return history

    @staticmethod
    def __is_exists(graph_state: StateSnapshot) -> bool:
        return graph_state.created_at is not None

    @staticmethod
    def __is_ended(graph_state: StateSnapshot) -> bool:
        return not any(graph_state.next)