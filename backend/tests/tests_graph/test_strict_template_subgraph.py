import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.core.chat_graph.strict_template_subgraph import StrictTemplateSubgraph
from src.dto.messages import ChatMessage


class TestStrictTemplateSubgraph:
    def test_subgraph_initialization(self):
        subgraph = StrictTemplateSubgraph()
        assert subgraph is not None

    @pytest.mark.asyncio
    async def test_setup_loop(self):
        subgraph = StrictTemplateSubgraph()

        mock_file_service = MagicMock()
        mock_file_service.extract_text = MagicMock(return_value="template text")
        mock_llm_use_cases = MagicMock()
        mock_llm_use_cases.setup_strict_template_loop = MagicMock(return_value=[ChatMessage.from_ai("Setup complete")])

        state = {
            "messages": [ChatMessage.from_user("Test")],
            "relevant_template": {"id": 1, "name": "strict"}
        }

        with patch('src.core.chat_graph.strict_template_subgraph.llm_use_cases', mock_llm_use_cases):
            result = await subgraph._StrictTemplateSubgraph__setup_loop(state, mock_file_service)

            assert "messages" in result
            assert len(result["messages"]) == 2

    @pytest.mark.asyncio
    async def test_invoke_llm_completion(self):
        subgraph = StrictTemplateSubgraph()

        mock_llm = AsyncMock()
        mock_llm_use_cases = AsyncMock()
        mock_llm_use_cases.loop_iteration_async = AsyncMock(return_value=(True, ChatMessage.from_ai("Ready")))

        state = {"messages": [ChatMessage.from_user("Test")]}

        with patch('src.core.chat_graph.strict_template_subgraph.llm_use_cases', mock_llm_use_cases):
            result = await subgraph._StrictTemplateSubgraph__invoke_llm(state, mock_llm)

            assert "loop_completed" in result
            assert result["loop_completed"] is True

    @pytest.mark.asyncio
    async def test_prepare_field_values_strict(self):
        subgraph = StrictTemplateSubgraph()

        mock_llm = AsyncMock()
        mock_llm_use_cases = AsyncMock()
        mock_llm_use_cases.prepare_strict_template_values_async = AsyncMock(return_value={"field1": "value1"})

        state = {
            "messages": [ChatMessage.from_user("Test")],
            "relevant_template": {"id": 1}
        }

        with patch('src.core.chat_graph.strict_template_subgraph.llm_use_cases', mock_llm_use_cases):
            result = await subgraph._StrictTemplateSubgraph__prepare_field_values(state, mock_llm)

            assert "field_values" in result
            assert result["field_values"]["field1"] == "value1"

    @pytest.mark.asyncio
    async def test_generate_document(self):
        subgraph = StrictTemplateSubgraph()

        mock_file_service = MagicMock()
        mock_file_service.fill_with_values = MagicMock()
        mock_result_storage = MagicMock()
        mock_result_file = MagicMock()
        mock_result_storage.write_issue_result_file = MagicMock(return_value=mock_result_file)

        state = {
            "issue_id": 1,
            "messages": [ChatMessage.from_user("Test")],
            "relevant_template": {"id": 1},
            "field_values": {"field1": "value1"}
        }

        result = await subgraph._StrictTemplateSubgraph__generate_document(state, mock_file_service,
                                                                           mock_result_storage)

        assert "success" in result
        assert result["success"] is True
        assert len(result["messages"]) == 2
        mock_file_service.fill_with_values.assert_called_once()