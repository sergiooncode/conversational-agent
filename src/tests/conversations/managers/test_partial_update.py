from unittest import mock
from unittest.mock import AsyncMock

from asgiref.sync import sync_to_async
import pytest

from agent.conversations.managers.partial_update import ConversationPartialUpdateManager
from agent.conversations.models import Conversation
from tests.conftest import async_return

pytest_plugins = ("pytest_asyncio",)
pytestmark = pytest.mark.django_db


class TestConversationPartialUpdateManager:

    @pytest.mark.asyncio
    async def test_partial_update_successful(self, valid_conversation):
        with mock.patch(
            "agent.conversations.managers.partial_update.AgentService",
            return_value=AsyncMock(),
        ) as agent_service_mock:
            agent_instance_mock = AsyncMock()
            agent_service_mock.return_value = agent_instance_mock
            result_mock = AsyncMock()
            agent_instance_mock.run.return_value = result_mock
            result_mock.final_output = await async_return("how can i help?")
            bot_message = await ConversationPartialUpdateManager(
                context={"message": "i have an issue"}
            ).partial_update(conversation_id=valid_conversation.id)

        assert bot_message == "how can i help?"

        actual_conversation = await Conversation.objects.aget(pk=valid_conversation.id)
        assert actual_conversation.raw_conversation == [
            {
                "content": "i have an issue",
                "role": "user",
            },
            {
                "content": "how can i help?",
                "role": "assistant",
            },
        ]

    @pytest.mark.asyncio
    async def test_partial_update_successful_with_sentiment_label(
        self, valid_conversation
    ):
        with mock.patch(
            "agent.conversations.managers.partial_update.AgentService",
            return_value=AsyncMock(),
        ) as agent_service_mock:
            agent_instance_mock = AsyncMock()
            agent_service_mock.return_value = agent_instance_mock
            result_mock = AsyncMock()
            agent_instance_mock.run.return_value = result_mock
            result_mock.final_output = await async_return("how can i help?")
            bot_message = await ConversationPartialUpdateManager(
                context={"message": "i have an issue and i am very annoyed"}
            ).partial_update(conversation_id=valid_conversation.id)

        assert bot_message == "how can i help?"

        actual_conversation = await Conversation.objects.aget(pk=valid_conversation.id)
        assert actual_conversation.raw_conversation == [
            {
                "content": "[User Sentiment: frustrated]\nUser: i have "
                "an issue and i am very annoyed",
                "role": "user",
            },
            {
                "content": "how can i help?",
                "role": "assistant",
            },
        ]
