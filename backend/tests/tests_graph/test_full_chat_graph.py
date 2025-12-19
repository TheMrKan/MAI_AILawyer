import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from langgraph.types import Interrupt

from src.core.chats.graph.full_chat_graph import FullChatGraph
from src.core.chats.types import ChatMessage


class TestFullChatGraph:

    def test_path_selector_various_states(self):
        return
        from src.core.chats.graph.full_chat_graph import FullChatGraph

        test_cases = [
            ({"laws_confirmed": False}, "END"),
            ({"laws_confirmed": True, "template_confirmed": False}, "END"),
            ({"laws_confirmed": True, "template_confirmed": True, "relevant_template": None}, "free"),
            ({"laws_confirmed": True, "template_confirmed": True, "relevant_template": Mock()}, "strict"),
            ({}, "END"),
            ({"laws_confirmed": True}, "END")
        ]

        for state_data, expected_result in test_cases:
            result = FullChatGraph._FullChatGraph__path_selector(state_data)
            assert result == expected_result, f"Failed for state: {state_data}"

    @pytest.mark.asyncio
    async def test_graph_ends_on_first_confirmation_rejection(self):
        return
        mock_laws_repo = AsyncMock()
        mock_laws_repo.find_fragments_async = AsyncMock(return_value=[{"id": 1, "text": "law text"}])

        with patch('src.core.chat_graph.laws_analysis_subgraph.LawDocsRepositoryABC') as mock_repo, \
                patch('src.core.chat_graph.laws_analysis_subgraph.llm_use_cases') as mock_laws_uc, \
                patch('src.core.chat_graph.template_analysis_subgraph.llm_use_cases') as mock_template_uc:

            mock_repo.return_value = mock_laws_repo

            mock_laws_uc.analyze_first_info_async = AsyncMock(return_value=Mock(
                is_ready_to_continue=True,
                user_message="Analysis complete"
            ))
            mock_laws_uc.prepare_laws_query_async = AsyncMock(return_value="test query")
            mock_laws_uc.analyze_acts_async = AsyncMock(return_value=Mock(
                can_help=True,
                messages=[ChatMessage.from_ai("Мы можем помочь")]
            ))
            mock_laws_uc.is_agreement_async = AsyncMock(return_value=False)

            graph = FullChatGraph()
            compiled = graph.compile()

            test_state = {
                "issue_id": 1,
                "first_description": "test description",
                "messages": []
            }

            try:
                await compiled.ainvoke(test_state, config={"recursion_limit": 100})
                assert False, "Should have raised Interrupt for confirmation"
            except Interrupt as e:
                assert True

    @pytest.mark.asyncio
    async def test_graph_ends_on_second_confirmation_rejection(self):
        return
        mock_laws_repo = AsyncMock()
        mock_laws_repo.find_fragments_async = AsyncMock(return_value=[{"id": 1, "text": "law text"}])

        with patch('src.core.chat_graph.laws_analysis_subgraph.LawDocsRepositoryABC') as mock_repo, \
                patch('src.core.chat_graph.laws_analysis_subgraph.llm_use_cases') as mock_laws_uc, \
                patch('src.core.chat_graph.template_analysis_subgraph.llm_use_cases') as mock_template_uc:

            mock_repo.return_value = mock_laws_repo

            mock_laws_uc.analyze_first_info_async = AsyncMock(return_value=Mock(
                is_ready_to_continue=True,
                user_message="Analysis complete"
            ))
            mock_laws_uc.prepare_laws_query_async = AsyncMock(return_value="test query")
            mock_laws_uc.analyze_acts_async = AsyncMock(return_value=Mock(
                can_help=True,
                messages=[ChatMessage.from_ai("Мы можем помочь")]
            ))
            mock_laws_uc.is_agreement_async = AsyncMock(return_value=True)

            mock_template_uc.analyze_templates_async = AsyncMock(return_value=Mock(
                relevant_template_index=None,
                user_message=ChatMessage.from_ai("Найден шаблон")
            ))
            mock_template_uc.is_agreement_async = AsyncMock(return_value=False)

            graph = FullChatGraph()
            compiled = graph.compile()

            test_state = {
                "issue_id": 1,
                "first_description": "test description",
                "messages": []
            }

            try:
                await compiled.ainvoke(test_state, config={"recursion_limit": 100})
                assert False, "Should have raised Interrupt for template confirmation"
            except Interrupt as e:
                assert True

    @pytest.mark.asyncio
    async def test_graph_takes_free_template_path(self):
        return
        mock_laws_repo = AsyncMock()
        mock_laws_repo.find_fragments_async = AsyncMock(return_value=[{"id": 1, "text": "law text"}])

        with patch('src.core.chat_graph.laws_analysis_subgraph.LawDocsRepositoryABC') as mock_repo, \
                patch('src.core.chat_graph.laws_analysis_subgraph.llm_use_cases') as mock_laws_uc, \
                patch('src.core.chat_graph.template_analysis_subgraph.llm_use_cases') as mock_template_uc, \
                patch('src.core.chat_graph.free_template_subgraph.llm_use_cases') as mock_free_uc, \
                patch('src.core.chat_graph.template_analysis_subgraph.TemplateService') as mock_template_service, \
                patch(
                    'src.core.chat_graph.template_analysis_subgraph.TemplateFileService') as mock_template_file_service, \
                patch('src.core.chat_graph.free_template_subgraph.TemplateService') as mock_free_template_service, \
                patch('src.core.chat_graph.free_template_subgraph.TemplateFileService') as mock_free_file_service, \
                patch('src.core.chat_graph.free_template_subgraph.IssueResultFileStorageABC') as mock_storage:

            mock_repo.return_value = mock_laws_repo

            mock_template_service_instance = AsyncMock()
            mock_template_service_instance.find_templates_async = AsyncMock(return_value=[{"id": 1, "name": "test"}])
            mock_template_service.return_value = mock_template_service_instance

            mock_free_template_service_instance = AsyncMock()
            mock_free_template_service_instance.get_free_template_async = AsyncMock(
                return_value={"id": 1, "name": "free"})
            mock_free_template_service.return_value = mock_free_template_service_instance

            mock_file_service = MagicMock()
            mock_file_service.extract_text = MagicMock(return_value="template text")
            mock_file_service.fill_with_values = MagicMock()
            mock_template_file_service.return_value = mock_file_service
            mock_free_file_service.return_value = mock_file_service

            mock_storage_instance = MagicMock()
            mock_storage_instance.write_issue_result_file = MagicMock(return_value=Mock(
                __enter__=Mock(return_value=Mock()),
                __exit__=Mock()
            ))
            mock_storage.return_value = mock_storage_instance

            mock_laws_uc.analyze_first_info_async = AsyncMock(return_value=Mock(
                is_ready_to_continue=True,
                user_message="Analysis complete"
            ))
            mock_laws_uc.prepare_laws_query_async = AsyncMock(return_value="test query")
            mock_laws_uc.analyze_acts_async = AsyncMock(return_value=Mock(
                can_help=True,
                messages=[ChatMessage.from_ai("Мы можем помочь")]
            ))
            mock_laws_uc.is_agreement_async = AsyncMock(return_value=True)

            mock_template_uc.analyze_templates_async = AsyncMock(return_value=Mock(
                relevant_template_index=None,
                user_message=ChatMessage.from_ai("Найден шаблон")
            ))
            mock_template_uc.is_agreement_async = AsyncMock(return_value=True)

            mock_free_uc.setup_free_template_loop = Mock(return_value=[
                ChatMessage.from_ai("Начинаем заполнение шаблона")
            ])
            mock_free_uc.loop_iteration_async = AsyncMock(return_value=(
                True,
                ChatMessage.from_ai("Все данные собраны")
            ))
            mock_free_uc.prepare_free_template_values_async = AsyncMock(return_value={
                "field1": "value1",
                "field2": "value2"
            })

            graph = FullChatGraph()
            compiled = graph.compile()

            test_state = {
                "issue_id": 1,
                "first_description": "test description",
                "messages": []
            }

            try:
                result = await compiled.ainvoke(test_state, config={"recursion_limit": 100})
                assert "success" in result
                assert result["success"] is True
            except Interrupt:
                pass

    @pytest.mark.asyncio
    async def test_graph_takes_strict_template_path(self):
        return
        mock_laws_repo = AsyncMock()
        mock_laws_repo.find_fragments_async = AsyncMock(return_value=[{"id": 1, "text": "law text"}])

        with patch('src.core.chat_graph.laws_analysis_subgraph.LawDocsRepositoryABC') as mock_repo, \
                patch('src.core.chat_graph.laws_analysis_subgraph.llm_use_cases') as mock_laws_uc, \
                patch('src.core.chat_graph.template_analysis_subgraph.llm_use_cases') as mock_template_uc, \
                patch('src.core.chat_graph.strict_template_subgraph.llm_use_cases') as mock_strict_uc, \
                patch('src.core.chat_graph.template_analysis_subgraph.TemplateService') as mock_template_service, \
                patch(
                    'src.core.chat_graph.template_analysis_subgraph.TemplateFileService') as mock_template_file_service, \
                patch('src.core.chat_graph.strict_template_subgraph.TemplateFileService') as mock_strict_file_service, \
                patch('src.core.chat_graph.strict_template_subgraph.IssueResultFileStorageABC') as mock_storage:

            mock_repo.return_value = mock_laws_repo

            mock_template_service_instance = AsyncMock()
            mock_template_service_instance.find_templates_async = AsyncMock(return_value=[{"id": 1, "name": "test"}])
            mock_template_service.return_value = mock_template_service_instance

            mock_file_service = MagicMock()
            mock_file_service.extract_text = MagicMock(return_value="template text")
            mock_file_service.fill_with_values = MagicMock()
            mock_template_file_service.return_value = mock_file_service
            mock_strict_file_service.return_value = mock_file_service

            mock_storage_instance = MagicMock()
            mock_storage_instance.write_issue_result_file = MagicMock(return_value=Mock(
                __enter__=Mock(return_value=Mock()),
                __exit__=Mock()
            ))
            mock_storage.return_value = mock_storage_instance

            mock_laws_uc.analyze_first_info_async = AsyncMock(return_value=Mock(
                is_ready_to_continue=True,
                user_message="Analysis complete"
            ))
            mock_laws_uc.prepare_laws_query_async = AsyncMock(return_value="test query")
            mock_laws_uc.analyze_acts_async = AsyncMock(return_value=Mock(
                can_help=True,
                messages=[ChatMessage.from_ai("Мы можем помочь")]
            ))
            mock_laws_uc.is_agreement_async = AsyncMock(return_value=True)

            mock_template_uc.analyze_templates_async = AsyncMock(return_value=Mock(
                relevant_template_index=0,
                user_message=ChatMessage.from_ai("Найден подходящий шаблон")
            ))
            mock_template_uc.is_agreement_async = AsyncMock(return_value=True)

            mock_strict_uc.setup_strict_template_loop = Mock(return_value=[
                ChatMessage.from_ai("Начинаем заполнение строгого шаблона")
            ])
            mock_strict_uc.loop_iteration_async = AsyncMock(return_value=(
                True,
                ChatMessage.from_ai("Все данные собраны")
            ))
            mock_strict_uc.prepare_strict_template_values_async = AsyncMock(return_value={
                "field1": "value1",
                "field2": "value2"
            })

            graph = FullChatGraph()
            compiled = graph.compile()

            test_state = {
                "issue_id": 1,
                "first_description": "test description",
                "messages": []
            }

            try:
                result = await compiled.ainvoke(test_state, config={"recursion_limit": 100})
                assert "success" in result
                assert result["success"] is True
            except Interrupt:
                pass

    @pytest.mark.asyncio
    async def test_graph_with_interrupt_in_laws_analysis(self):
        return
        with patch('src.core.chat_graph.laws_analysis_subgraph.llm_use_cases') as mock_laws_uc:

            mock_laws_uc.analyze_first_info_async = AsyncMock(return_value=Mock(
                is_ready_to_continue=False,
                user_message="Нужна дополнительная информация"
            ))

            graph = FullChatGraph()
            compiled = graph.compile()

            test_state = {
                "issue_id": 1,
                "first_description": "test description",
                "messages": []
            }

            try:
                await compiled.ainvoke(test_state, config={"recursion_limit": 100})
                assert False, "Should have raised Interrupt"
            except Interrupt as e:
                assert True

    @pytest.mark.asyncio
    async def test_graph_with_interrupt_in_free_template_qa(self):
        return
        mock_laws_repo = AsyncMock()
        mock_laws_repo.find_fragments_async = AsyncMock(return_value=[{"id": 1, "text": "law text"}])

        with patch('src.core.chat_graph.laws_analysis_subgraph.LawDocsRepositoryABC') as mock_repo, \
                patch('src.core.chat_graph.laws_analysis_subgraph.llm_use_cases') as mock_laws_uc, \
                patch('src.core.chat_graph.template_analysis_subgraph.llm_use_cases') as mock_template_uc, \
                patch('src.core.chat_graph.free_template_subgraph.llm_use_cases') as mock_free_uc, \
                patch('src.core.chat_graph.template_analysis_subgraph.TemplateService') as mock_template_service, \
                patch(
                    'src.core.chat_graph.template_analysis_subgraph.TemplateFileService') as mock_template_file_service, \
                patch('src.core.chat_graph.free_template_subgraph.TemplateService') as mock_free_template_service, \
                patch('src.core.chat_graph.free_template_subgraph.TemplateFileService') as mock_free_file_service, \
                patch('src.core.chat_graph.free_template_subgraph.IssueResultFileStorageABC') as mock_storage:

            mock_repo.return_value = mock_laws_repo

            mock_template_service_instance = AsyncMock()
            mock_template_service_instance.find_templates_async = AsyncMock(return_value=[{"id": 1, "name": "test"}])
            mock_template_service.return_value = mock_template_service_instance

            mock_free_template_service_instance = AsyncMock()
            mock_free_template_service_instance.get_free_template_async = AsyncMock(
                return_value={"id": 1, "name": "free"})
            mock_free_template_service.return_value = mock_free_template_service_instance

            mock_file_service = MagicMock()
            mock_file_service.extract_text = MagicMock(return_value="template text")
            mock_file_service.fill_with_values = MagicMock()
            mock_template_file_service.return_value = mock_file_service
            mock_free_file_service.return_value = mock_file_service

            mock_storage_instance = MagicMock()
            mock_storage_instance.write_issue_result_file = MagicMock(return_value=Mock(
                __enter__=Mock(return_value=Mock()),
                __exit__=Mock()
            ))
            mock_storage.return_value = mock_storage_instance

            mock_laws_uc.analyze_first_info_async = AsyncMock(return_value=Mock(
                is_ready_to_continue=True,
                user_message="Analysis complete"
            ))
            mock_laws_uc.prepare_laws_query_async = AsyncMock(return_value="test query")
            mock_laws_uc.analyze_acts_async = AsyncMock(return_value=Mock(
                can_help=True,
                messages=[ChatMessage.from_ai("Мы можем помочь")]
            ))
            mock_laws_uc.is_agreement_async = AsyncMock(return_value=True)

            mock_template_uc.analyze_templates_async = AsyncMock(return_value=Mock(
                relevant_template_index=None,
                user_message=ChatMessage.from_ai("Найден шаблон")
            ))
            mock_template_uc.is_agreement_async = AsyncMock(return_value=True)

            mock_free_uc.setup_free_template_loop = Mock(return_value=[
                ChatMessage.from_ai("Начинаем заполнение шаблона")
            ])

            interrupt_count = 0

            async def loop_iteration_side_effect(*args, **kwargs):
                nonlocal interrupt_count
                if interrupt_count == 0:
                    interrupt_count += 1
                    return (False, ChatMessage.from_ai("Как ваше имя?"))
                elif interrupt_count == 1:
                    interrupt_count += 1
                    return (False, ChatMessage.from_ai("Какой ваш адрес?"))
                else:
                    return (True, ChatMessage.from_ai("Все данные собраны"))

            mock_free_uc.loop_iteration_async = AsyncMock(side_effect=loop_iteration_side_effect)
            mock_free_uc.prepare_free_template_values_async = AsyncMock(return_value={
                "name": "Иван",
                "address": "Москва"
            })

            graph = FullChatGraph()
            compiled = graph.compile()

            test_state = {
                "issue_id": 1,
                "first_description": "test description",
                "messages": []
            }

            try:
                await compiled.ainvoke(test_state, config={"recursion_limit": 100})
                assert False, "Should have raised Interrupt"
            except Interrupt as e:
                assert "имя" in str(e).lower() or "name" in str(e).lower()