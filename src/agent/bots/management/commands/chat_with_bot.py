import asyncio
import json
import re
from uuid import UUID

import structlog
from agents import (
    HandoffOutputItem,
    ItemHelpers,
    MessageOutputItem,
    ToolCallItem,
    ToolCallOutputItem,
)
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

    async def run_agent(self, input: str):
        agent_service_2 = AgentService(
            name=BOT_FUNCTION_TO_PROMPT_MAP[BotFunction.CUSTOMER_SUPPORT.value][2][
                "name"
            ],
            instructions=BOT_FUNCTION_TO_PROMPT_MAP[BotFunction.CUSTOMER_SUPPORT.value][
                2
            ]["instructions"],
        )
        agent_service_1 = AgentService(
            name=BOT_FUNCTION_TO_PROMPT_MAP[BotFunction.CUSTOMER_SUPPORT.value][1][
                "name"
            ],
            instructions=BOT_FUNCTION_TO_PROMPT_MAP[BotFunction.CUSTOMER_SUPPORT.value][
                1
            ]["instructions"],
            tools=[collected_information],
            output_type=CollectedInfo,
            handoffs=[agent_service_2],
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
        return await agent_service_0.run(input=input)

    def _get_agent_response(self, conversation_history):
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(self.run_agent(conversation_history))
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
        conversation.raw_conversation.append({"role": "user", "content": user_input})
        casted_result = result.final_output
        if isinstance(result.final_output, CollectedInfo):
            casted_result = result.final_output.model_dump()
        conversation.raw_conversation.append(
            {"role": "assistant", "content": casted_result}
        )
        conversation.save()
        if summary:
            logger.info("update_raw_conversation_and_summary", message="summary saved")
            conversation.summary = summary
            conversation.save()

    def _stringify_conversation_history(self, history):
        conversation_history_text = ""
        for msg in reversed(history):
            role = msg["role"].capitalize()
            content = msg["content"]
            conversation_history_text += f"{role}: {content}\n\n"
        return conversation_history_text

    def _get_stringified_conversation_history(self, conversation_id: UUID):
        conversation_history = []
        try:
            conversation = Conversation.objects.get(pk=conversation_id)
            conversation_history = conversation.raw_conversation
        except Conversation.DoesNotExist as e:
            logger.warning("conversation_history", message=e)
            exit(1)
        return self._stringify_conversation_history(conversation_history)

    def handle(self, *args, **options) -> str | None:
        bot = Bot.objects.create(function=BotFunction.CUSTOMER_SUPPORT)
        human_user = HumanUser.objects.create()
        conversation = Conversation.objects.create(bot=bot, human_user=human_user)
        conversation_history = ""
        while True:
            try:
                user_input = input("User: ")
                if not conversation_history:
                    conversation_history = f"{user_input}\n\n"
                result = self._get_agent_response(conversation_history)
                print(f"Assistant: {result.final_output}\n\n")
                for new_item in result.new_items:
                    print("beginning ------------------------")
                    agent_name = new_item.agent.name
                    if isinstance(new_item, MessageOutputItem):
                        print(
                            f"{agent_name}: {ItemHelpers.text_message_output(new_item)}"
                        )
                    elif isinstance(new_item, HandoffOutputItem):
                        print(
                            f"Handed off from {new_item.source_agent.name} to {new_item.target_agent.name}"
                        )
                    elif isinstance(new_item, ToolCallItem):
                        print(f"{agent_name}: Calling a tool")
                    elif isinstance(new_item, ToolCallOutputItem):
                        print(f"{agent_name}: Tool call output: {new_item.output}")
                    else:
                        print(
                            f"{agent_name}: Skipping item: {new_item.__class__.__name__}"
                        )
                    print("end ------------------------")

                summary = self._parse_summary(result)

                self._update_raw_conversation_and_summary(
                    conversation, result, summary, user_input
                )
                conversation_history = self._get_stringified_conversation_history(
                    conversation.id
                )

                print(f"Conversation history: \n{conversation_history}")
            except Exception as e:
                import traceback

                traceback.print_exc()
                logger.warning("bots_chat_with_bot_cmd", message=str(e))
                continue
