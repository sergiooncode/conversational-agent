import json
import re
from dataclasses import dataclass, field
from typing import Dict, List
from uuid import UUID

import structlog

from agent.conversations.exceptions import ConversationNotFound
from agent.conversations.models import Conversation
from agent.services.conversational.openai.agents import (
    CollectedInfo,
)
from agent.services.conversational.openai.multiagent.controller import (
    CUSTOMER_SUPPORT_AGENT_MAP,
    MultiAgentController,
)

# from agent.services.rag.sbert_net.service import RagService
from agent.services.sentiment_analysis.detect import SentimentAnalysisDetectionService

logger = structlog.get_logger(__name__)


@dataclass
class ConversationPartialUpdateManager:
    context: Dict
    _conversation_history: str = field(init=False)

    async def partial_update(self, conversation_id: UUID):
        conversation_to_update = await self._get_conversation(conversation_id)
        self._conversation_history = self._get_stringified_conversation_history(
            conversation_to_update, self.context["message"]
        )
        logger.info("conversation history")
        logger.info(self._conversation_history)

        result = await self._run_conversation_service(self.context["message"])
        logger.info("result.final_output", message=result.final_output)

        summary = self._parse_summary(result)
        await self._update_raw_conversation_and_summary(
            conversation_to_update,
            result,
            summary,
            self.context["message"],
        )

        if isinstance(result.final_output, CollectedInfo):
            logger.info("adapting response")
            logger.info(result.final_output.model_dump())
            return (
                f"I received your details {result.final_output.model_dump()}, thanks!"
            )

        return result.final_output

    # def _rag_enrich_with_answers(self, user_message: str):
    #    service = RagService()
    #    return service.get_relevant_answers(user_message)

    def _stringify_conversation_history(self, history: List, user_message: str):
        conversation_history_text = f"{user_message}"
        for msg in reversed(history):
            role = msg["role"].capitalize()
            content = msg["content"]
            conversation_history_text += f"{role}: {content}\n\n"
        return conversation_history_text

    def _get_stringified_conversation_history(
        self, conversation: Conversation, user_message: str
    ):
        conversation_history = conversation.raw_conversation
        return self._stringify_conversation_history(conversation_history, user_message)

    def _detect_and_add_sentiment_label(self):
        return SentimentAnalysisDetectionService().detect_frustration(
            self.context["message"]
        )

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

    async def _update_raw_conversation_and_summary(
        self, conversation, result, summary, user_message
    ):
        conversation.raw_conversation.append({"role": "user", "content": user_message})
        casted_result = result.final_output
        if isinstance(result.final_output, CollectedInfo):
            casted_result = result.final_output.model_dump()
        conversation.raw_conversation.append(
            {"role": "assistant", "content": casted_result}
        )
        await conversation.asave()
        if summary:
            conversation.summary = summary
            await conversation.asave()
            logger.info(
                "partial_update_manager_update_summary", message="summary saved"
            )

    async def _update_raw_conversation(self, conversation_to_update, result):
        conversation_to_update.append(f"User: {self.context['message']}\n\n")
        conversation_to_update.append(f"Assistant: {result.final_output}\n\n")
        await conversation_to_update.asave()

    async def _get_conversation(self, conversation_id: UUID):
        try:
            return await Conversation.objects.aget(pk=conversation_id)
        except Conversation.DoesNotExist:
            raise ConversationNotFound()

    async def _run_conversation_service(self, user_message: str):
        controller = MultiAgentController(
            {
                "triaging_and_info_collector": CUSTOMER_SUPPORT_AGENT_MAP[
                    "triaging_and_info_collector"
                ],
                "info_structurer": CUSTOMER_SUPPORT_AGENT_MAP["info_structurer"],
                "user_reassurance_and_send_off": CUSTOMER_SUPPORT_AGENT_MAP[
                    "user_reassurance_and_send_off"
                ],
            }
        )
        agent_used, response = await controller.route(
            user_message, history=self._conversation_history
        )
        return response
