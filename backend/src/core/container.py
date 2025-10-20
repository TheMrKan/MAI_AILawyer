from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.llm import AbstractLLM
    from src.core.graph_controller import GraphController


class Container:
    LLM_instance: "AbstractLLM"
    graph_controller: "GraphController"

    @classmethod
    def build(cls):
        from src.core.llm import CerebrasLLM
        cls.LLM_instance = CerebrasLLM()

        from src.core.graph_controller import GraphController
        from langgraph.checkpoint.memory import InMemorySaver
        checkpointer = InMemorySaver()
        cls.graph_controller = GraphController(checkpointer)