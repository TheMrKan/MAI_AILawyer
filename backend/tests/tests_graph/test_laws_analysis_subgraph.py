import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.core.chat_graph.laws_analysis_subgraph import LawsAnalysisSubgraph
from src.dto.messages import ChatMessage


class TestLawsAnalysisSubgraph:
    def test_subgraph_initialization(self):
        subgraph = LawsAnalysisSubgraph()
        assert subgraph is not None

    @pytest.mark.asyncio
    async def test_save_first_info(self):
        subgraph = LawsAnalysisSubgraph()
        input_state = {
            "issue_id": 1,
            "first_description": "Test description"
        }

        result = await subgraph._LawsAnalysisSubgraph__save_first_info(input_state)

        assert "messages" in result
        assert len(result["messages"]) == 2
        assert result["messages"][0].role == "system"
        assert result["messages"][1].content == "Test description"

    @pytest.mark.asyncio
    async def test_analyze_info_completion(self):
        subgraph = LawsAnalysisSubgraph()

        mock_llm = AsyncMock()
        mock_result = MagicMock()
        mock_result.is_ready_to_continue = True
        mock_llm_use_cases = AsyncMock()
        mock_llm_use_cases.analyze_first_info_async = AsyncMock(return_value=mock_result)

        state = {"messages": [ChatMessage.from_user("Test")]}

        with patch('src.core.chat_graph.laws_analysis_subgraph.llm_use_cases', mock_llm_use_cases):
            result = await subgraph._LawsAnalysisSubgraph__analyze_info(state, mock_llm)

            assert "first_info_completed" in result
            assert result["first_info_completed"] is True

    @pytest.mark.asyncio
    async def test_find_law_documents(self):
        subgraph = LawsAnalysisSubgraph()

        mock_llm = AsyncMock()
        mock_repo = AsyncMock()
        mock_llm_use_cases = AsyncMock()
        mock_llm_use_cases.prepare_laws_query_async = AsyncMock(return_value="test query")
        mock_repo.find_fragments_async = AsyncMock(return_value=[{"doc": "test"}])

        state = {"messages": [ChatMessage.from_user("Test")]}

        with patch('src.core.chat_graph.laws_analysis_subgraph.llm_use_cases', mock_llm_use_cases):
            result = await subgraph._LawsAnalysisSubgraph__find_law_documents(state, mock_llm, mock_repo)

            assert "law_docs" in result
            assert len(result["law_docs"]) == 1

    def test_continue_if_true_wrapper(self):
        subgraph = LawsAnalysisSubgraph()

        wrapper = subgraph._LawsAnalysisSubgraph__continue_if_true("can_help")

        state_true = {"can_help": True}
        state_false = {"can_help": False}

        assert wrapper(state_true) == "continue"
        assert wrapper(state_false) == "END"