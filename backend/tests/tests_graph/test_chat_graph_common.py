import pytest
from unittest.mock import AsyncMock, MagicMock
from langgraph.types import Interrupt
from src.core.chat_graph.common import create_process_confirmation_node
from src.dto.messages import ChatMessage


class TestProcessConfirmationNode:
    @pytest.mark.asyncio
    async def test_confirmation_node_positive_response(self):
        mock_llm = AsyncMock()
        mock_llm_use_cases = AsyncMock()
        mock_llm_use_cases.is_agreement_async = AsyncMock(return_value=True)

        mock_logger = MagicMock()
        node_func = create_process_confirmation_node("test_key", mock_logger)

        original_state = {"messages": [ChatMessage.from_ai("Test message")]}

        mock_interrupt = MagicMock()
        mock_interrupt.return_value = "да, согласен"

        with pytest.raises(Interrupt):
            result = await node_func(original_state, mock_llm)

        mock_logger.info.assert_called_once()

    @pytest.mark.asyncio
    async def test_confirmation_node_negative_response(self):
        mock_llm = AsyncMock()
        mock_llm_use_cases = AsyncMock()
        mock_llm_use_cases.is_agreement_async = AsyncMock(return_value=False)

        mock_logger = MagicMock()
        node_func = create_process_confirmation_node("test_key", mock_logger)

        original_state = {"messages": []}

        with pytest.raises(Interrupt):
            await node_func(original_state, mock_llm)

    def test_state_type_definitions(self):
        from src.core.chat_graph.common import InputState, BaseState, FreeTemplateState, StrictTemplateState

        input_state_fields = {"issue_id", "first_description"}
        base_state_fields = {"messages", "first_info_completed", "law_docs", "can_help",
                             "laws_confirmed", "templates", "relevant_template",
                             "template_confirmed", "field_values", "success"}

        assert input_state_fields.issubset(set(InputState.__annotations__.keys()))
        assert base_state_fields.issubset(set(BaseState.__annotations__.keys()))
        assert "loop_completed" in FreeTemplateState.__annotations__
        assert "loop_completed" in StrictTemplateState.__annotations__
        assert "fields" in StrictTemplateState.__annotations__