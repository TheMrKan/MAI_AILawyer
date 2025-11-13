from typing import TypedDict
import logging
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
import asyncio

from src.core.chat_graph.states import BaseState, InputState
from src.core.chat_graph.laws_analysis_subgraph import LawsAnalysisSubgraph
from src.core.chat_graph.template_analysis_subgraph import TemplateAnalysisSubgraph


logger = logging.getLogger(__name__)


class FullChatGraph(StateGraph[BaseState, None, InputState, BaseState]):

    def __init__(self):
        super().__init__(BaseState, input_schema=InputState)    # type: ignore
        self.__build()

    def __build(self):
        self.add_edge(START, "laws_analysis_subgraph")
        self.add_node("laws_analysis_subgraph", LawsAnalysisSubgraph().compile())
        self.add_conditional_edges("laws_analysis_subgraph", lambda state: state["laws_confirmed"], {
            True: "template_analysis_subgraph",
            False: END
        })

        self.add_node("template_analysis_subgraph", TemplateAnalysisSubgraph().compile())
        self.add_conditional_edges("template_analysis_subgraph", self.__path_selector, {
            "free": END,
            "strict": END,
        })

    @staticmethod
    def __path_selector(state: BaseState) -> str:
        if not state["laws_confirmed"]:
            return "END"

        if "free" in state["relevant_template"]:
            return "free"
        return "strict"



