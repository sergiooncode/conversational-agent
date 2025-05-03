import asyncio
from django.core.management import BaseCommand, CommandParser
import structlog

from agent.bots.models import BotFunction, Bot
from agent.conversations.models import Conversation
from agent.human_users.models import HumanUser
from agent.prompts.models import BOT_FUNCTION_TO_PROMPT_MAP
from agent.services.llm.openai.agents import AgentService

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

    def handle(self, *args, **options) -> str | None:
        bot = Bot.objects.create(function=BotFunction.CUSTOMER_SUPPORT)
        human_user = HumanUser.objects.create()
        conversation = Conversation.objects.create(bot=bot, human_user=human_user)
        while True:
            try:
                previous_raw_conversation_updated = conversation.raw_conversation[
                    "conversation"
                ]
                user_input = input("Customer: ")
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(self.run_agent(user_input))
                previous_raw_conversation_updated.append(f"Human user: {user_input}")
                previous_raw_conversation_updated.append(
                    f"Agent: {result.final_output}"
                )
                conversation.transcript = {
                    "conversation": previous_raw_conversation_updated
                }
                conversation.save()
                print(f"Agent: {result.final_output}")
            except Exception as e:
                logger.warning("bots_chat_with_bot_cmd", message=str(e))
                continue
