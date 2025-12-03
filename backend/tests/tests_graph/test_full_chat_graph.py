import pytest
from unittest.mock import Mock, patch, MagicMock
from langgraph.graph import StateGraph

from src.core.chat_graph.full_chat_graph import FullChatGraph


@pytest.fixture
def mock_subgraphs():
    with patch('src.core.chat_graph.full_chat_graph.LawsAnalysisSubgraph') as mock_laws, \
            patch('src.core.chat_graph.full_chat_graph.TemplateAnalysisSubgraph') as mock_template, \
            patch('src.core.chat_graph.full_chat_graph.FreeTemplateSubgraph') as mock_free, \
            patch('src.core.chat_graph.full_chat_graph.StrictTemplateSubgraph') as mock_strict:
        mock_laws_instance = MagicMock()
        mock_laws_instance.compile.return_value = "laws_compiled"
        mock_laws.return_value = mock_laws_instance

        mock_template_instance = MagicMock()
        mock_template_instance.compile.return_value = "template_compiled"
        mock_template.return_value = mock_template_instance

        mock_free_instance = MagicMock()
        mock_free_instance.compile.return_value = "free_compiled"
        mock_free.return_value = mock_free_instance

        mock_strict_instance = MagicMock()
        mock_strict_instance.compile.return_value = "strict_compiled"
        mock_strict.return_value = mock_strict_instance

        yield {
            'laws': mock_laws_instance,
            'template': mock_template_instance,
            'free': mock_free_instance,
            'strict': mock_strict_instance
        }


@pytest.fixture
def full_chat_graph(mock_subgraphs):
    return FullChatGraph()


class TestFullChatGraph:
    def test_initialization(self, full_chat_graph):
        assert isinstance(full_chat_graph, StateGraph)
        assert full_chat_graph.nodes is not None

    def test_graph_contains_all_nodes(self, full_chat_graph, mock_subgraphs):
        assert "laws_analysis_subgraph" in full_chat_graph.nodes
        assert "template_analysis_subgraph" in full_chat_graph.nodes
        assert "free_template_subgraph" in full_chat_graph.nodes
        assert "strict_template_subgraph" in full_chat_graph.nodes

        mock_subgraphs['laws'].compile.assert_called_once()
        mock_subgraphs['template'].compile.assert_called_once()
        mock_subgraphs['free'].compile.assert_called_once()
        mock_subgraphs['strict'].compile.assert_called_once()

    @pytest.mark.parametrize("state_data,expected_result", [
        ({"laws_confirmed": False}, "END"),
        ({"laws_confirmed": True, "template_confirmed": False}, "END"),
        ({"laws_confirmed": True, "template_confirmed": True, "relevant_template": None}, "free"),
        ({"laws_confirmed": True, "template_confirmed": True, "relevant_template": Mock()}, "strict"),
        ({}, "END"),  # Missing laws_confirmed defaults to False
        ({"laws_confirmed": True}, "END"),  # Missing template_confirmed
    ])
    def test_path_selector_various_states(self, state_data, expected_result):
        from src.core.chat_graph.full_chat_graph import FullChatGraph

        result = FullChatGraph._FullChatGraph__path_selector(state_data)
        assert result == expected_result

    def test_path_selector_with_real_template_object(self):
        from src.core.chat_graph.full_chat_graph import FullChatGraph

        template_mock = Mock()
        state = {"laws_confirmed": True, "template_confirmed": True, "relevant_template": template_mock}
        result = FullChatGraph._FullChatGraph__path_selector(state)
        assert result == "strict"

    def test_path_selector_with_falsy_template(self):
        from src.core.chat_graph.full_chat_graph import FullChatGraph

        state = {"laws_confirmed": True, "template_confirmed": True, "relevant_template": False}
        result = FullChatGraph._FullChatGraph__path_selector(state)
        assert result == "free"

    def test_path_selector_with_empty_template(self):
        from src.core.chat_graph.full_chat_graph import FullChatGraph

        state = {"laws_confirmed": True, "template_confirmed": True, "relevant_template": ""}
        result = FullChatGraph._FullChatGraph__path_selector(state)
        assert result == "free"

    def test_graph_edge_conditions(self, full_chat_graph):
        from src.core.chat_graph.full_chat_graph import FullChatGraph

        assert hasattr(full_chat_graph, '_conditional_edges')
        assert "laws_analysis_subgraph" in full_chat_graph._conditional_edges
        assert "template_analysis_subgraph" in full_chat_graph._conditional_edges

    def test_graph_has_start_and_end_nodes(self, full_chat_graph):
        assert hasattr(full_chat_graph, 'start_node')
        assert hasattr(full_chat_graph, 'end_node')

    def test_build_method_creates_correct_structure(self, mock_subgraphs):
        with patch.object(FullChatGraph, '_FullChatGraph__build') as mock_build:
            graph = FullChatGraph()
            mock_build.assert_called_once()
            assert isinstance(graph, FullChatGraph)

    @patch('langgraph.graph.StateGraph.add_node')
    @patch('langgraph.graph.StateGraph.add_edge')
    @patch('langgraph.graph.StateGraph.add_conditional_edges')
    def test_build_method_invokes_graph_methods(self, mock_add_conditional, mock_add_edge, mock_add_node,
                                                mock_subgraphs):
        graph = FullChatGraph()

        assert mock_add_node.call_count >= 4
        assert mock_add_edge.call_count >= 1
        assert mock_add_conditional.call_count >= 1

    def test_graph_is_compilable(self, full_chat_graph):
        compiled_graph = full_chat_graph.compile()
        assert compiled_graph is not None
        assert hasattr(compiled_graph, 'invoke')

    @pytest.mark.asyncio
    async def test_graph_invocation_with_valid_state(self, full_chat_graph):
        compiled = full_chat_graph.compile()

        test_state = {
            "issue_id": 1,
            "first_description": "test description",
            "messages": [],
            "laws_confirmed": True,
            "template_confirmed": True,
            "relevant_template": None
        }

        result = await compiled.ainvoke(test_state)
        assert result is not None

    def test_graph_input_schema(self, full_chat_graph):
        assert hasattr(full_chat_graph, 'input_schema')
        assert full_chat_graph.input_schema is not None

    def test_graph_state_class(self, full_chat_graph):
        from src.core.chat_graph.common import BaseState
        assert full_chat_graph.state_schema == BaseState

    @pytest.mark.parametrize("missing_field", ["laws_confirmed", "template_confirmed"])
    def test_path_selector_missing_fields(self, missing_field):
        from src.core.chat_graph.full_chat_graph import FullChatGraph

        state = {"laws_confirmed": True, "template_confirmed": True, "relevant_template": None}
        state.pop(missing_field)

        result = FullChatGraph._FullChatGraph__path_selector(state)
        assert result == "END"