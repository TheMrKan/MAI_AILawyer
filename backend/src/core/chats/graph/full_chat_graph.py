import logging
from langgraph.graph import StateGraph, START, END

from src.core.chats.graph.common import BaseState, InputState
from src.core.chats.graph.laws_analysis_subgraph import LawsAnalysisSubgraph
from src.core.chats.graph.template_analysis_subgraph import TemplateAnalysisSubgraph
from src.core.chats.graph.free_template_subgraph import FreeTemplateSubgraph
from src.core.chats.graph.strict_template_subgraph import StrictTemplateSubgraph


logger = logging.getLogger(__name__)


class FullChatGraph(StateGraph[BaseState, None, InputState, BaseState]):

    def __init__(self):
        super().__init__(BaseState, input_schema=InputState)    # type: ignore
        self.__build()

    def __build(self):
        self.add_edge(START, "laws_analysis_subgraph")
        self.add_node("laws_analysis_subgraph", LawsAnalysisSubgraph().compile())
        self.add_conditional_edges("laws_analysis_subgraph", lambda state: state.get("laws_confirmed", False), {
            True: "template_analysis_subgraph",
            False: END
        })

        self.add_node("template_analysis_subgraph", TemplateAnalysisSubgraph().compile())
        self.add_conditional_edges("template_analysis_subgraph", self.__path_selector, {
            "free": "free_template_subgraph",
            "strict": "strict_template_subgraph",
            "END": END
        })

        self.add_node("free_template_subgraph", FreeTemplateSubgraph().compile())
        self.add_node("strict_template_subgraph", StrictTemplateSubgraph().compile())

    @staticmethod
    def __path_selector(state: BaseState) -> str:
        if not state.get("template_confirmed", False):
            return "END"

        if state.get("relevant_template", None):
            return "strict"
        return "free"



