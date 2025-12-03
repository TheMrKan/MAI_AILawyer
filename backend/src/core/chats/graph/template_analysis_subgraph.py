from langgraph.graph import StateGraph, START
import logging

from src.core.chats.graph.common import BaseState, create_process_confirmation_node
from src.core.llm import LLMABC, use_cases
from src.core.templates.manager import TemplateManager
from src.core.templates.content_service import TemplateContentService
from src.application.provider import inject_global


class TemplateAnalysisSubgraph(StateGraph[BaseState, None, BaseState, BaseState]):

    __logger: logging.Logger

    def __init__(self):
        super().__init__(BaseState)    # type: ignore
        self.__logger = logging.getLogger(self.__class__.__name__)

        self.__build()

    def __build(self):
        self.add_edge(START, "find_templates")
        self.add_node("find_templates", self.__find_templates)
        self.add_edge("find_templates", "analyze_templates")
        self.add_node("analyze_templates", self.__analyze_templates)
        self.add_edge("analyze_templates", "confirm1")
        self.add_node("confirm1", create_process_confirmation_node("template_confirmed", self.__logger))

    @inject_global
    async def __find_templates(self, state: BaseState, service: TemplateManager) -> BaseState:
        self.__logger.info("Searching for templates...")
        templates = await service.find_templates_async(state["first_description"])
        self.__logger.info(f"Found templates: {templates}")
        return {"templates": templates}

    @inject_global
    async def __analyze_templates(self, state: BaseState, service: TemplateContentService, llm: LLMABC) -> BaseState:
        self.__logger.info("Analyzing templates...")
        texts = [service.extract_text(tpl) for tpl in state["templates"]]

        result = await llm_use_cases.analyze_templates_async(llm, state["messages"], texts)
        relevant = state["templates"][result.relevant_template_index] if result.relevant_template_index is not None else None

        self.__logger.info("Selected relevant template: %s", relevant)
        return {"relevant_template": relevant, "messages": [*state["messages"], result.user_message]}
