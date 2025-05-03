from typing import List

import structlog
from agents import Agent, Runner, handoff
from agents import set_default_openai_key
from django.conf import settings

from agent.services.exceptions import (
    OpenAIAgentNotConfiguredException,
    OpenAIAgentRuntimeException,
    OpenAIAgentEmptyUserInputException,
)

logger = structlog.get_logger(__name__)

set_default_openai_key(settings.OPENAPI_API_KEY)


class AgentService:
    def __init__(
        self,
        name: str | None = None,
        instructions: str | None = None,
        tools: str | None = None,
        handoffs: List = [],
    ):
        if any(arg is None for arg in [name, instructions]):
            raise OpenAIAgentNotConfiguredException()

        additional_config = {}
        if tools:
            additional_config["tools"] = tools
        if handoffs:
            additional_config["handoffs"] = [
                handoff(h.agent, on_handoff=self._on_handoff_call) for h in handoffs
            ]

        self._agent = Agent(name=name, instructions=instructions, **additional_config)

    @property
    def agent(self):
        return self._agent

    def _on_handoff_call(*args):
        logger.info("on_handoff_call", message=args)

    async def run(self, user_input: str | None):
        if not user_input:
            raise OpenAIAgentEmptyUserInputException()

        try:
            return await Runner.run(self._agent, user_input)
        except Exception as e:
            logger.warning("openai_llm_agent_service", message=str(e))
            raise OpenAIAgentRuntimeException()
