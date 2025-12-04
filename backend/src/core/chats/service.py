from langgraph.checkpoint.memory import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command, StateSnapshot
import logging
from dataclasses import dataclass

from src.core.chats.graph.full_chat_graph import FullChatGraph, InputState
from src.core.chats.types import ChatMessage
from src.application.provider import Registerable, Provider, Singleton


class GraphError(Exception):
    pass


@dataclass
class IssueChatState:
    messages: list[ChatMessage]
    is_ended: bool
    success: bool


class IssueChatService(Registerable):

    @classmethod
    async def on_build_provider(cls, provider: Provider):
        checkpointer = provider[BaseCheckpointSaver]
        provider.register(IssueChatService, Singleton(cls(checkpointer)))

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

    async def get_state(self, issue_id: int) -> IssueChatState:
        graph_config = {"configurable": {"thread_id": issue_id}}
        graph_state = await self.graph.aget_state(graph_config, subgraphs=True)

        if not self.__is_exists(graph_state):
            raise KeyError("Чат не существует")

        return IssueChatState(
            self.__get_chat_history(graph_state),
            self.__is_ended(graph_state),
            self.__is_success(graph_state)
        )

    async def process_new_user_message(self, issue_id: int, message_text: str) -> IssueChatState:
        graph_config = {"configurable": {"thread_id": issue_id}}
        graph_state = await self.graph.aget_state(graph_config, subgraphs=True)

        skip_messages = 0

        if not self.__is_exists(graph_state):
            graph_input = InputState(issue_id=issue_id, first_description=message_text)
        elif self.__is_ended(graph_state):
            raise GraphError("Чат завершен")
        else:
            graph_input = Command(resume=message_text)
            history = self.__get_chat_history(graph_state)
            skip_messages = len(history)

        result = await self.graph.ainvoke(graph_input, graph_config, subgraphs=True)

        messages = result["messages"]

        if result["messages"][0].role.value == "system":
            messages = result["messages"][skip_messages:]

        graph_state = await self.graph.aget_state(graph_config, subgraphs=True)

        return IssueChatState(
            messages,
            self.__is_ended(graph_state),
            self.__is_success(graph_state)
        )

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

    @staticmethod
    def __is_success(graph_state: StateSnapshot) -> bool:
        success = graph_state.values.get("success", False)
        if not success and any(graph_state.tasks):
            success = graph_state.tasks[0].state.values.get("success", False)
        return success
