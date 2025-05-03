import asyncio
import re
import json

import structlog
from django.core.management import BaseCommand, CommandParser

from agent.bots.models import BotFunction, Bot
from agent.conversations.models import Conversation
from agent.human_users.models import HumanUser
from agent.prompts.models import BOT_FUNCTION_TO_PROMPT_MAP
from agent.services.llm.openai.agents import (
    AgentService,
    collected_information,
    CollectedInfo,
)

logger = structlog.get_logger(__name__)


class Command(BaseCommand):
    help = "Chat with a Customer Support bot"

    def add_arguments(self, parser: CommandParser) -> None:
        pass

    async def run_agent(self, user_input: str):
        agent_service_1 = AgentService(
            name=BOT_FUNCTION_TO_PROMPT_MAP[BotFunction.CUSTOMER_SUPPORT.value][1][
                "name"
            ],
            instructions=BOT_FUNCTION_TO_PROMPT_MAP[BotFunction.CUSTOMER_SUPPORT.value][
                1
            ]["instructions"],
            tools=[collected_information],
            output_type=CollectedInfo,
        )
        agent_service_0 = AgentService(
            name=BOT_FUNCTION_TO_PROMPT_MAP[BotFunction.CUSTOMER_SUPPORT.value][0][
                "name"
            ],
            instructions=BOT_FUNCTION_TO_PROMPT_MAP[BotFunction.CUSTOMER_SUPPORT.value][
                0
            ]["instructions"],
            handoffs=[agent_service_1],
        )
        return await agent_service_0.run(user_input)

    def _get_agent_response(self, user_input):
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.run_agent(user_input))
        return result

    def _parse_json_block(self, text):
        # Find content between ```json and ```
        pattern = r"```json\s*(\{.*?\})\s*```"
        match = re.search(pattern, text, re.DOTALL)

        if match:
            json_text = match.group(1)
            return json.loads(json_text)
        else:
            raise ValueError("No JSON found in text")

    def _parse_summary(self, result):
        summary = None
        if isinstance(result.final_output, CollectedInfo):
            summary = result.final_output.model_dump()
            return summary

        try:
            summary = self._parse_json_block(result.final_output)
        except ValueError as e:
            logger.warning("", message=f"Not parsed correctly {e}")
        return summary

    def _update_raw_conversation_and_summary(
        self, conversation, result, summary, user_input
    ):
        previous_raw_conversation_updated = conversation.raw_conversation[
            "conversation"
        ]
        previous_raw_conversation_updated.append(f"Human user: {user_input}")
        previous_raw_conversation_updated.append(f"Agent: {result.final_output}")
        conversation.raw_conversation = {
            "conversation": previous_raw_conversation_updated
        }
        if summary:
            conversation.summary = {"summary": summary}
        conversation.save()

    def handle(self, *args, **options) -> str | None:
        bot = Bot.objects.create(function=BotFunction.CUSTOMER_SUPPORT)
        human_user = HumanUser.objects.create()
        conversation = Conversation.objects.create(bot=bot, human_user=human_user)
        while True:
            try:
                user_input = input("Customer: ")
                result = self._get_agent_response(user_input)

                summary = self._parse_summary(result)

                self._update_raw_conversation_and_summary(
                    conversation, result, summary, user_input
                )

                print(f"Agent: {result.final_output}")
            except Exception as e:
                logger.warning("bots_chat_with_bot_cmd", message=str(e))
                continue
