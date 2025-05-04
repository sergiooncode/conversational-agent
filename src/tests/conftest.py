import asyncio
import pytest
import pytest_asyncio
from rest_framework.test import APIClient

from agent.bots.models import Bot
from agent.conversations.models import Conversation
from agent.human_users.models import HumanUser


@pytest.fixture(scope="session")
def api_client():
    yield APIClient()


@pytest_asyncio.fixture
async def valid_conversation():
    bot = await Bot.objects.acreate(function="CUSTOMER_SUPPORT")
    human_user = await HumanUser.objects.acreate()
    conversation = await Conversation.objects.acreate(bot=bot, human_user=human_user)
    yield conversation


@pytest.fixture
def valid_bot_message():
    return (
        "I’m sorry to hear that. Could you please provide more "
        "details about the issue you’re experiencing? If you have "
        "an order number, that would be helpful as well."
    )


def async_return(result):
    f = asyncio.Future()
    f.set_result(result)
    return f
