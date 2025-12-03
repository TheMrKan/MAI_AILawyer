from langgraph.graph import StateGraph, START
from langgraph.types import interrupt
import logging

from src.core.chats.graph.common import BaseState, FreeTemplateState
from src.core.templates.service import TemplateService
from src.core.templates.file_service import TemplateFileService
from src.core.results.iface import IssueResultFileStorageABC
from src.core.llm import LLMABC, use_cases
from src.core.chats.types import ChatMessage
from src.application.provider import inject_global


class FreeTemplateSubgraph(StateGraph[FreeTemplateState, None, BaseState, FreeTemplateState]):

    __logger: logging.Logger

    def __init__(self):
        super().__init__(BaseState)    # type: ignore
        self.__logger = logging.getLogger(self.__class__.__name__)

        self.__build()

    def __build(self):
        self.add_edge(START, "setup_loop")
        self.add_node("setup_loop", self.__setup_loop)
        self.add_edge("setup_loop", "invoke_llm")

        self.add_node("invoke_llm", self.__invoke_llm)
        self.add_conditional_edges("invoke_llm", lambda state: state.get("loop_completed", False), {
            False: "get_user_answer",
            True: "prepare_field_values"
        })
        self.add_node("get_user_answer", self.__handle_answer)
        self.add_edge("get_user_answer", "invoke_llm"),

        self.add_node("prepare_field_values", self.__prepare_field_values)
        self.add_edge("prepare_field_values", "generate_document")

        self.add_node("generate_document", self.__generate_document)

    @inject_global
    async def __setup_loop(self,
                           state: BaseState,
                           service: TemplateService,
                           file_service: TemplateFileService) -> FreeTemplateState:
        self.__logger.debug("Setting up QA loop...")

        free_template = await service.get_free_template_async()
        text = file_service.extract_text(free_template)

        return {"messages": state["messages"] + llm_use_cases.setup_free_template_loop(free_template, text), "relevant_template": free_template}

    @inject_global
    async def __invoke_llm(self, state: FreeTemplateState, llm: LLMABC) -> FreeTemplateState:
        self.__logger.debug("Asking...")
        is_ready, message = await llm_use_cases.loop_iteration_async(llm, state["messages"])
        if is_ready:
            return {"loop_completed": True}

        return {"messages": [*state["messages"], message]}

    def __handle_answer(self, state: FreeTemplateState) -> FreeTemplateState:
        user_input = interrupt(None)
        user_message = ChatMessage.from_user(user_input)
        self.__logger.debug("Got user answer: %s", user_input)

        return {"messages": [*state["messages"], user_message]}

    @inject_global
    async def __prepare_field_values(self, state: FreeTemplateState, llm: LLMABC) -> FreeTemplateState:
        self.__logger.debug("Preparing field values...")
        values = await llm_use_cases.prepare_free_template_values_async(llm, state["messages"], state["relevant_template"])
        self.__logger.debug("Prepared field values: %s", values)

        return {"field_values": values}

    @inject_global
    async def __generate_document(self,
                                  state: FreeTemplateState,
                                  file_service: TemplateFileService,
                                  result_storage: IssueResultFileStorageABC) -> FreeTemplateState:
        self.__logger.debug("Generating document...")

        with result_storage.write_issue_result_file(state["issue_id"]) as result_file:
            file_service.fill_with_values(state["relevant_template"], state["field_values"], result_file)

        self.__logger.debug("Document generated")
        return {"messages": [*state["messages"],
                             ChatMessage.from_ai("Ваш документ готов!\nСпасибо, что воспользовались нашим сервисом!")],
                "success": True}
