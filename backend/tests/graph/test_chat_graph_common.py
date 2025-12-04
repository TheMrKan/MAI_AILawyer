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