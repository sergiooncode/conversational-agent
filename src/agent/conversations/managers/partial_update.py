from dataclasses import dataclass
from typing import Dict
from uuid import UUID

import structlog

from agent.bots.models import BotFunction
from agent.conversations.exceptions import ConversationNotFound
from agent.conversations.models import Conversation
from agent.prompts.models import BOT_FUNCTION_TO_PROMPT_MAP
from agent.services.llm.openai.agents import AgentService

logger = structlog.get_logger(__name__)


@dataclass
class ConversationPartialUpdateManager:
    context: Dict

    async def partial_update(self, conversation_id: UUID):
        conversation_to_update = await self._get_conversation(conversation_id)
        previous_raw_conversation_updated = conversation_to_update.raw_conversation[
            "conversation"
        ]
        result = await self._run_conversation_service(self.context["message"])
        await self._update_raw_conversation(
            conversation_to_update, previous_raw_conversation_updated, result
        )

        return result.final_output

    async def _update_raw_conversation(
        self, conversation_to_update, previous_raw_conversation_updated, result
    ):
        previous_raw_conversation_updated.append(
            f"Human user: {self.context['message']}"
        )
        previous_raw_conversation_updated.append(f"Agent: {result.final_output}")
        conversation_to_update.raw_conversation = {
            "conversation": previous_raw_conversation_updated
        }
        await conversation_to_update.asave()

    async def _get_conversation(self, conversation_id: UUID):
        try:
            return await Conversation.objects.aget(pk=conversation_id)
        except Conversation.DoesNotExist as e:
            raise ConversationNotFound from e

    async def _run_conversation_service(self, message: str):
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
        return await agent_service_0.run(message)
