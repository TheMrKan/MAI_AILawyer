import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from langgraph.types import Interrupt

from src.core.chat_graph.full_chat_graph import FullChatGraph
from src.core.chat_graph.laws_analysis_subgraph import LawsAnalysisSubgraph
from src.core.chat_graph.template_analysis_subgraph import TemplateAnalysisSubgraph
from src.core.chat_graph.free_template_subgraph import FreeTemplateSubgraph
from src.core.chat_graph.strict_template_subgraph import StrictTemplateSubgraph
from src.dto.messages import ChatMessage


@pytest.fixture
def mock_subgraphs():
    with patch('src.core.chat_graph.full_chat_graph.LawsAnalysisSubgraph') as mock_laws, \
            patch('src.core.chat_graph.full_chat_graph.TemplateAnalysisSubgraph') as mock_template, \
            patch('src.core.chat_graph.full_chat_graph.FreeTemplateSubgraph') as mock_free, \
            patch('src.core.chat_graph.full_chat_graph.StrictTemplateSubgraph') as mock_strict:
        mock_laws_instance = MagicMock(spec=LawsAnalysisSubgraph)
        mock_laws_instance.compile.return_value = AsyncMock()
        mock_laws.return_value = mock_laws_instance

        mock_template_instance = MagicMock(spec=TemplateAnalysisSubgraph)
        mock_template_instance.compile.return_value = AsyncMock()
        mock_template.return_value = mock_template_instance

        mock_free_instance = MagicMock(spec=FreeTemplateSubgraph)
        mock_free_instance.compile.return_value = AsyncMock()
        mock_free.return_value = mock_free_instance

        mock_strict_instance = MagicMock(spec=StrictTemplateSubgraph)
        mock_strict_instance.compile.return_value = AsyncMock()
        mock_strict.return_value = mock_strict_instance

        yield {
            'laws': mock_laws_instance,
            'template': mock_template_instance,
            'free': mock_free_instance,
            'strict': mock_strict_instance
        }


class TestFullChatGraph:

    @pytest.mark.asyncio
    async def test_graph_with_real_interrupt_in_laws_analysis(self):
        with patch('src.core.chat_graph.full_chat_graph.LawsAnalysisSubgraph') as MockLawsSubgraph:
            mock_laws_instance = MagicMock()
            mock_laws_compiled = AsyncMock()

            def raise_interrupt(state):
                raise Interrupt("Need more info about the situation")

            mock_laws_compiled.ainvoke = AsyncMock(side_effect=raise_interrupt)
            mock_laws_instance.compile.return_value = mock_laws_compiled
            MockLawsSubgraph.return_value = mock_laws_instance

            with patch('src.core.chat_graph.full_chat_graph.TemplateAnalysisSubgraph'):
                with patch('src.core.chat_graph.full_chat_graph.FreeTemplateSubgraph'):
                    with patch('src.core.chat_graph.full_chat_graph.StrictTemplateSubgraph'):
                        graph = FullChatGraph()
                        compiled = graph.compile()

                        test_state = {
                            "issue_id": 1,
                            "first_description": "Меня уволили без объяснения причин",
                            "messages": []
                        }

                        try:
                            await compiled.ainvoke(test_state)
                            assert False, "Should have raised Interrupt"
                        except Interrupt as e:
                            assert "Need more info about the situation" in str(e)

    @pytest.mark.asyncio
    async def test_graph_with_interrupt_in_free_template_qa(self):
        with patch('src.core.chat_graph.full_chat_graph.LawsAnalysisSubgraph') as MockLawsSubgraph:
            mock_laws_instance = MagicMock()
            mock_laws_compiled = AsyncMock()
            mock_laws_compiled.ainvoke = AsyncMock(return_value={
                "laws_confirmed": True,
                "messages": [ChatMessage.from_user("Меня уволили")],
                "first_info_completed": True
            })
            mock_laws_instance.compile.return_value = mock_laws_compiled
            MockLawsSubgraph.return_value = mock_laws_instance

            with patch('src.core.chat_graph.full_chat_graph.TemplateAnalysisSubgraph') as MockTemplateSubgraph:
                mock_template_instance = MagicMock()
                mock_template_compiled = AsyncMock()
                mock_template_compiled.ainvoke = AsyncMock(return_value={
                    "template_confirmed": True,
                    "relevant_template": None,
                    "messages": [ChatMessage.from_user("Меня уволили"), ChatMessage.from_ai("Найден шаблон")]
                })
                mock_template_instance.compile.return_value = mock_template_compiled
                MockTemplateSubgraph.return_value = mock_template_instance

                with patch('src.core.chat_graph.full_chat_graph.FreeTemplateSubgraph') as MockFreeSubgraph:
                    mock_free_instance = MagicMock()
                    mock_free_compiled = AsyncMock()

                    interrupt_count = 0

                    async def free_template_with_interrupts(state):
                        nonlocal interrupt_count
                        if interrupt_count == 0:
                            interrupt_count += 1
                            raise Interrupt("Как ваше полное имя?")
                        elif interrupt_count == 1:
                            interrupt_count += 1
                            raise Interrupt("Какой ваш адрес?")
                        else:
                            return {
                                "success": True,
                                "field_values": {"name": "Иван Иванов", "address": "Москва"},
                                "messages": state["messages"] + [ChatMessage.from_ai("Документ готов!")]
                            }

                    mock_free_compiled.ainvoke = AsyncMock(side_effect=free_template_with_interrupts)
                    mock_free_instance.compile.return_value = mock_free_compiled
                    MockFreeSubgraph.return_value = mock_free_instance

                    with patch('src.core.chat_graph.full_chat_graph.StrictTemplateSubgraph'):
                        graph = FullChatGraph()
                        compiled = graph.compile()

                        test_state = {
                            "issue_id": 1,
                            "first_description": "Меня уволили",
                            "messages": []
                        }

                        try:
                            await compiled.ainvoke(test_state)
                            assert False, "Should have raised Interrupt"
                        except Interrupt as e:
                            assert "Как ваше полное имя?" in str(e)

                        updated_state = {
                            "issue_id": 1,
                            "first_description": "Меня уволили",
                            "messages": [ChatMessage.from_user("Иван Иванов")]
                        }

                        try:
                            await compiled.ainvoke(updated_state)
                            assert False, "Should have raised Interrupt again"
                        except Interrupt as e:
                            assert "Какой ваш адрес?" in str(e)

                        final_state = {
                            "issue_id": 1,
                            "first_description": "Меня уволили",
                            "messages": [ChatMessage.from_user("Иван Иванов"), ChatMessage.from_user("Москва")]
                        }

                        result = await compiled.ainvoke(final_state)
                        assert result["success"] is True
                        assert result["field_values"]["name"] == "Иван Иванов"

    @pytest.mark.asyncio
    async def test_graph_with_interrupt_for_user_confirmation(self):
        with patch('src.core.chat_graph.full_chat_graph.LawsAnalysisSubgraph') as MockLawsSubgraph:
            mock_laws_instance = MagicMock()
            mock_laws_compiled = AsyncMock()

            confirmation_interrupt = False

            async def laws_with_confirmation(state):
                nonlocal confirmation_interrupt
                if not confirmation_interrupt:
                    confirmation_interrupt = True
                    raise Interrupt("Вы согласны с анализом законодательства?")
                return {
                    "laws_confirmed": True,
                    "messages": state["messages"] + [ChatMessage.from_user("да, согласен")]
                }

            mock_laws_compiled.ainvoke = AsyncMock(side_effect=laws_with_confirmation)
            mock_laws_instance.compile.return_value = mock_laws_compiled
            MockLawsSubgraph.return_value = mock_laws_instance

            with patch('src.core.chat_graph.full_chat_graph.TemplateAnalysisSubgraph'):
                with patch('src.core.chat_graph.full_chat_graph.FreeTemplateSubgraph'):
                    with patch('src.core.chat_graph.full_chat_graph.StrictTemplateSubgraph'):
                        graph = FullChatGraph()
                        compiled = graph.compile()

                        test_state = {
                            "issue_id": 1,
                            "first_description": "Не выплатили зарплату",
                            "messages": []
                        }

                        try:
                            await compiled.ainvoke(test_state)
                            assert False, "Should have raised Interrupt for confirmation"
                        except Interrupt as e:
                            assert "Вы согласны с анализом законодательства?" in str(e)

                        state_with_response = {
                            "issue_id": 1,
                            "first_description": "Не выплатили зарплату",
                            "messages": [ChatMessage.from_user("да, согласен")]
                        }

                        result = await compiled.ainvoke(state_with_response)
                        assert result["laws_confirmed"] is True

    @pytest.mark.asyncio
    async def test_graph_handles_multiple_interrupts_in_strict_template(self):
        with patch('src.core.chat_graph.full_chat_graph.LawsAnalysisSubgraph') as MockLawsSubgraph:
            mock_laws_instance = MagicMock()
            mock_laws_compiled = AsyncMock()
            mock_laws_compiled.ainvoke = AsyncMock(return_value={
                "laws_confirmed": True,
                "messages": [ChatMessage.from_user("Требую восстановления")]
            })
            mock_laws_instance.compile.return_value = mock_laws_compiled
            MockLawsSubgraph.return_value = mock_laws_instance

            with patch('src.core.chat_graph.full_chat_graph.TemplateAnalysisSubgraph') as MockTemplateSubgraph:
                mock_template_instance = MagicMock()
                mock_template_compiled = AsyncMock()
                mock_template_compiled.ainvoke = AsyncMock(return_value={
                    "template_confirmed": True,
                    "relevant_template": {"id": 1, "name": "Исковое заявление"},
                    "messages": [ChatMessage.from_user("Требую восстановления")]
                })
                mock_template_instance.compile.return_value = mock_template_compiled
                MockTemplateSubgraph.return_value = mock_template_instance

                with patch('src.core.chat_graph.full_chat_graph.StrictTemplateSubgraph') as MockStrictSubgraph:
                    mock_strict_instance = MagicMock()
                    mock_strict_compiled = AsyncMock()

                    field_count = 0
                    fields_needed = ["дата увольнения", "должность", "стаж работы"]

                    async def strict_template_with_fields(state):
                        nonlocal field_count
                        if field_count < len(fields_needed):
                            field_name = fields_needed[field_count]
                            field_count += 1
                            raise Interrupt(f"Укажите {field_name}")

                        return {
                            "success": True,
                            "field_values": {
                                "дата увольнения": "2024-01-15",
                                "должность": "Инженер",
                                "стаж работы": "3 года"
                            },
                            "messages": state["messages"] + [ChatMessage.from_ai("Документ сформирован")]
                        }

                    mock_strict_compiled.ainvoke = AsyncMock(side_effect=strict_template_with_fields)
                    mock_strict_instance.compile.return_value = mock_strict_compiled
                    MockStrictSubgraph.return_value = mock_strict_instance

                    with patch('src.core.chat_graph.full_chat_graph.FreeTemplateSubgraph'):
                        graph = FullChatGraph()
                        compiled = graph.compile()

                        test_state = {
                            "issue_id": 1,
                            "first_description": "Незаконное увольнение",
                            "messages": []
                        }

                        responses = [
                            "2024-01-15",
                            "Инженер",
                            "3 года"
                        ]

                        current_state = test_state.copy()

                        for i, response in enumerate(responses):
                            try:
                                await compiled.ainvoke(current_state)
                                assert False, f"Should have raised Interrupt for field {fields_needed[i]}"
                            except Interrupt as e:
                                assert fields_needed[i] in str(e).lower()
                                current_state["messages"] = current_state.get("messages", []) + [
                                    ChatMessage.from_user(response)]

                        result = await compiled.ainvoke(current_state)
                        assert result["success"] is True
                        assert result["field_values"]["должность"] == "Инженер"

    @pytest.mark.asyncio
    async def test_graph_interrupt_handling_with_state_persistence(self):
        with patch('src.core.chat_graph.full_chat_graph.LawsAnalysisSubgraph') as MockLawsSubgraph:
            mock_laws_instance = MagicMock()
            mock_laws_compiled = AsyncMock()

            has_interrupted = False

            async def laws_analysis_with_state_persistence(state):
                nonlocal has_interrupted
                if not has_interrupted:
                    has_interrupted = True
                    raise Interrupt("Нужны дополнительные детали")

                assert "user_response" in state
                assert state["user_response"] == "Работал 2 года"
                return {
                    "laws_confirmed": True,
                    "messages": state["messages"],
                    "first_info_completed": True
                }

            mock_laws_compiled.ainvoke = AsyncMock(side_effect=laws_analysis_with_state_persistence)
            mock_laws_instance.compile.return_value = mock_laws_compiled
            MockLawsSubgraph.return_value = mock_laws_instance

            with patch('src.core.chat_graph.full_chat_graph.TemplateAnalysisSubgraph'):
                with patch('src.core.chat_graph.full_chat_graph.FreeTemplateSubgraph'):
                    with patch('src.core.chat_graph.full_chat_graph.StrictTemplateSubgraph'):
                        graph = FullChatGraph()
                        compiled = graph.compile()

                        initial_state = {
                            "issue_id": 1,
                            "first_description": "Сокращение",
                            "messages": [],
                            "user_response": None
                        }

                        try:
                            await compiled.ainvoke(initial_state)
                            assert False, "Should have raised Interrupt"
                        except Interrupt:
                            pass

                        updated_state = {
                            "issue_id": 1,
                            "first_description": "Сокращение",
                            "messages": [ChatMessage.from_user("Работал 2 года")],
                            "user_response": "Работал 2 года"
                        }

                        result = await compiled.ainvoke(updated_state)
                        assert result["laws_confirmed"] is True

    def test_path_selector_various_states(self):
        from src.core.chat_graph.full_chat_graph import FullChatGraph

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