from unittest import mock

import pytest

from agent.conversations.managers.partial_update import ConversationPartialUpdateManager
from tests.conftest import async_return

pytest_plugins = ("pytest_asyncio",)
pytestmark = pytest.mark.django_db


class TestConversationPartialUpdateManager:

    @pytest.mark.asyncio
    async def test_partial_update_successful(self, valid_conversation):
        with mock.patch(
            "agent.conversations.managers.partial_update.AgentService"
        ) as agent_service_mock:
            bot_message = await ConversationPartialUpdateManager(
                context={"message": "i have an issue"}
            ).partial_update(conversation_id=valid_conversation.id)

        assert bot_message == ""
