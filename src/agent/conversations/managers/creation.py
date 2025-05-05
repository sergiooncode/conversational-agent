from dataclasses import dataclass
from typing import Dict
from uuid import UUID

import structlog

from agent.bots.models import INPUTTED_FUNCTION_TO_BOT_FUNCTION_MAP, Bot
from agent.conversations.exceptions import (
    ConversationNotFound,
    ConversationSummaryDoesntExist,
)
from agent.conversations.models import Conversation
from agent.human_users.models import HumanUser
from agent.services.text_to_speech.eleven_labs.service import TextToSpeechService
from agent.settings.base import text_to_speech_text_template

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


@dataclass
class ConversationCreateFollowupSpeechManager:
    def create(self, conversation_id: UUID):
        conversation = self._get_conversation(conversation_id)
        if not conversation.summary:
            raise ConversationSummaryDoesntExist()

        text_to_convert = self._generate_follow_up_text(conversation)
        path_to_recording = self._invoke_text_to_speech(text_to_convert)
        return path_to_recording

    def _get_conversation(self, conversation_id: UUID):
        try:
            return Conversation.objects.get(pk=conversation_id)
        except Conversation.DoesNotExist:
            raise ConversationNotFound()

    def _generate_follow_up_text(self, conversation: Conversation):
        summary = conversation.summary
        return text_to_speech_text_template(summary)

    def _invoke_text_to_speech(self, text_to_convert: str):
        path_to_recording = TextToSpeechService().convert_and_save_to_file(
            text_to_convert
        )
        return path_to_recording
