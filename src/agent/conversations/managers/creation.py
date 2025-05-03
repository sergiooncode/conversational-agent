from dataclasses import dataclass
from typing import Dict
import structlog

from agent.bots.models import INPUTTED_FUNCTION_TO_BOT_FUNCTION_MAP, Bot
from agent.conversations.models import Conversation
from agent.human_users.models import HumanUser

logger = structlog.get_logger(__name__)


@dataclass
class ConversationCreationManager:
    context: Dict

    def create(self):
        bot = Bot.objects.create(
            function=INPUTTED_FUNCTION_TO_BOT_FUNCTION_MAP[self.context["function"]]
        )
        human_user = HumanUser.objects.create()
        conversation = Conversation.objects.create(bot=bot, human_user=human_user)
        return conversation
