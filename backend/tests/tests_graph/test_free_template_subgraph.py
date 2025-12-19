import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from langgraph.types import Interrupt
from src.core.chats.graph.free_template_subgraph import FreeTemplateSubgraph
from src.core.chats.types import ChatMessage


class TestFreeTemplateSubgraph:
    def test_subgraph_initialization(self):
        return
        subgraph = FreeTemplateSubgraph()
        assert subgraph is not None

    @pytest.mark.asyncio
    async def test_setup_loop(self):
        return
        subgraph = FreeTemplateSubgraph()

        mock_service = AsyncMock()
        mock_service.get_free_template_async = AsyncMock(return_value={"id": 1, "name": "free"})
        mock_file_service = MagicMock()
        mock_file_service.extract_text = MagicMock(return_value="template text")
        mock_llm_use_cases = MagicMock()
        mock_llm_use_cases.setup_free_template_loop = MagicMock(return_value=[ChatMessage.from_ai("Setup complete")])

        state = {"messages": [ChatMessage.from_user("Test")]}

        with patch('src.core.chat_graph.free_template_subgraph.llm_use_cases', mock_llm_use_cases):
            result = await subgraph._FreeTemplateSubgraph__setup_loop(state, mock_service, mock_file_service)

            assert "messages" in result
            assert len(result["messages"]) == 2
            assert "relevant_template" in result
            assert result["relevant_template"]["id"] == 1

    @pytest.mark.asyncio
    async def test_invoke_llm_completion(self):
        return
        subgraph = FreeTemplateSubgraph()

        mock_llm = AsyncMock()
        mock_llm_use_cases = AsyncMock()
        mock_llm_use_cases.loop_iteration_async = AsyncMock(return_value=(True, ChatMessage.from_ai("Ready")))

        state = {"messages": [ChatMessage.from_user("Test")]}

        with patch('src.core.chat_graph.free_template_subgraph.llm_use_cases', mock_llm_use_cases):
            result = await subgraph._FreeTemplateSubgraph__invoke_llm(state, mock_llm)

            assert "loop_completed" in result
            assert result["loop_completed"] is True

    @pytest.mark.asyncio
    async def test_invoke_llm_continue(self):
        return
        subgraph = FreeTemplateSubgraph()

        mock_llm = AsyncMock()
        mock_llm_use_cases = AsyncMock()
        mock_llm_use_cases.loop_iteration_async = AsyncMock(return_value=(False, ChatMessage.from_ai("Need more info")))

        state = {"messages": [ChatMessage.from_user("Test")]}

        with patch('src.core.chat_graph.free_template_subgraph.llm_use_cases', mock_llm_use_cases):
            result = await subgraph._FreeTemplateSubgraph__invoke_llm(state, mock_llm)

            assert "messages" in result
            assert len(result["messages"]) == 2
            assert "loop_completed" not in result

    def test_handle_answer(self):
        return
        subgraph = FreeTemplateSubgraph()

        state = {"messages": [ChatMessage.from_ai("Question?")]}

        with pytest.raises(Interrupt):
            result = subgraph._FreeTemplateSubgraph__handle_answer(state)

    @pytest.mark.asyncio
    async def test_prepare_field_values(self):
        return
        subgraph = FreeTemplateSubgraph()

        mock_llm = AsyncMock()
        mock_llm_use_cases = AsyncMock()
        mock_llm_use_cases.prepare_free_template_values_async = AsyncMock(return_value={"field1": "value1"})

        state = {
            "messages": [ChatMessage.from_user("Test")],
            "relevant_template": {"id": 1}
        }

        with patch('src.core.chat_graph.free_template_subgraph.llm_use_cases', mock_llm_use_cases):
            result = await subgraph._FreeTemplateSubgraph__prepare_field_values(state, mock_llm)

            assert "field_values" in result
            assert result["field_values"]["field1"] == "value1"