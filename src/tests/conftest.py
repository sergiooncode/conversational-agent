import asyncio
import pytest
from rest_framework.test import APIClient

from agent.bots.models import Bot
from agent.conversations.models import Conversation
from agent.human_users.models import HumanUser


@pytest.fixture(scope="session")
def api_client():
    yield APIClient()


@pytest.fixture
def valid_conversation():
    bot = Bot.objects.create(function="CUSTOMER_SUPPORT")
    human_user = HumanUser.objects.create()
    conversation = Conversation.objects.create(bot=bot, human_user=human_user)
    return conversation


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
