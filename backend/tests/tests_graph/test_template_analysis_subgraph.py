import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.core.chat_graph.template_analysis_subgraph import TemplateAnalysisSubgraph
from src.dto.messages import ChatMessage


class TestTemplateAnalysisSubgraph:
    def test_subgraph_initialization(self):
        subgraph = TemplateAnalysisSubgraph()
        assert subgraph is not None

    @pytest.mark.asyncio
    async def test_find_templates(self):
        subgraph = TemplateAnalysisSubgraph()

        mock_service = AsyncMock()
        mock_service.find_templates_async = AsyncMock(return_value=[{"id": 1, "name": "test"}])

        state = {"first_description": "Test description"}

        result = await subgraph._TemplateAnalysisSubgraph__find_templates(state, mock_service)

        assert "templates" in result
        assert len(result["templates"]) == 1
        assert result["templates"][0]["id"] == 1

    @pytest.mark.asyncio
    async def test_analyze_templates_with_relevant(self):
        subgraph = TemplateAnalysisSubgraph()

        mock_file_service = MagicMock()
        mock_file_service.extract_text = MagicMock(return_value="template text")
        mock_llm = AsyncMock()
        mock_llm_use_cases = AsyncMock()

        mock_result = MagicMock()
        mock_result.relevant_template_index = 0
        mock_result.user_message = ChatMessage.from_ai("Test analysis")
        mock_llm_use_cases.analyze_templates_async = AsyncMock(return_value=mock_result)

        templates = [{"id": 1, "name": "test"}, {"id": 2, "name": "test2"}]
        state = {
            "templates": templates,
            "messages": [ChatMessage.from_user("Test")]
        }

        with patch('src.core.chat_graph.template_analysis_subgraph.llm_use_cases', mock_llm_use_cases):
            result = await subgraph._TemplateAnalysisSubgraph__analyze_templates(state, mock_file_service, mock_llm)

            assert "relevant_template" in result
            assert result["relevant_template"] == templates[0]
            assert len(result["messages"]) == 2

    @pytest.mark.asyncio
    async def test_analyze_templates_without_relevant(self):
        subgraph = TemplateAnalysisSubgraph()

        mock_file_service = MagicMock()
        mock_file_service.extract_text = MagicMock(return_value="template text")
        mock_llm = AsyncMock()
        mock_llm_use_cases = AsyncMock()

        mock_result = MagicMock()
        mock_result.relevant_template_index = None
        mock_result.user_message = ChatMessage.from_ai("Test analysis")
        mock_llm_use_cases.analyze_templates_async = AsyncMock(return_value=mock_result)

        templates = [{"id": 1, "name": "test"}]
        state = {
            "templates": templates,
            "messages": [ChatMessage.from_user("Test")]
        }

        with patch('src.core.chat_graph.template_analysis_subgraph.llm_use_cases', mock_llm_use_cases):
            result = await subgraph._TemplateAnalysisSubgraph__analyze_templates(state, mock_file_service, mock_llm)

            assert "relevant_template" in result
            assert result["relevant_template"] is None