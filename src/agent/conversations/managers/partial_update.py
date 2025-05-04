import json
import re
from dataclasses import dataclass
from typing import Dict
from uuid import UUID

import structlog

from agent.bots.models import BotFunction
from agent.conversations.exceptions import ConversationNotFound
from agent.conversations.models import Conversation
from agent.prompts.models import BOT_FUNCTION_TO_PROMPT_MAP
from agent.services.llm.openai.agents import (
    AgentService,
    CollectedInfo,
)

logger = structlog.get_logger(__name__)


@dataclass
class ConversationPartialUpdateManager:
    context: Dict

    async def partial_update(self, conversation_id: UUID):
        conversation_to_update = await self._get_conversation(conversation_id)
        result = await self._run_conversation_service(self.context["message"])

        summary = self._parse_summary(result)
        await self._update_raw_conversation_and_summary(
            conversation_to_update, result, summary, self.context["message"]
        )

        return result.final_output

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
        self, conversation, result, summary, user_message
    ):
        conversation.raw_conversation.append({"role": "user", "content": user_message})
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

    async def _update_raw_conversation(self, conversation_to_update, result):
        conversation_to_update.append(f"User: {self.context['message']}")
        conversation_to_update.append(f"Assistant: {result.final_output}")
        await conversation_to_update.asave()

    async def _get_conversation(self, conversation_id: UUID):
        try:
            return await Conversation.objects.aget(pk=conversation_id)
        except Conversation.DoesNotExist:
            raise ConversationNotFound()

    async def _run_conversation_service(self, user_message: str):
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
        return await agent_service_0.run(user_message)
