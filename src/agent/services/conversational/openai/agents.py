from typing import List

import structlog
from agents import Agent, Runner, handoff, function_tool
from agents import set_default_openai_key
from django.conf import settings
from agents.extensions.handoff_prompt import (
    RECOMMENDED_PROMPT_PREFIX as BASE_PROMPT,
)  # noqa
from pydantic import BaseModel

from agent.services.exceptions import (
    OpenAIAgentNotConfiguredException,
    OpenAIAgentRuntimeException,
    OpenAIAgentEmptyUserInputException,
)

logger = structlog.get_logger(__name__)

set_default_openai_key(settings.OPENAPI_API_KEY)


@function_tool
def collected_information(
    order_number: str,
    problem_category: str,
    problem_description: str,
    urgency_level: str,
):
    result = {
        "order_number": order_number,
        "problem_category": problem_category,
        "problem_description": problem_description,
        "urgency_level": urgency_level,
    }
    return result


class CollectedInfo(BaseModel):
    order_number: str
    problem_category: str
    problem_description: str
    urgency_level: str


class AgentService:
    def __init__(
        self,
        name: str | None = None,
        instructions: str | None = None,
        tools: str | None = None,
        handoffs: List = [],
        output_type: str | None = None,
        output_schema_strict: bool | None = None,
    ):
        if any(arg is None for arg in [name, instructions]):
            raise OpenAIAgentNotConfiguredException()

        additional_config = {}
        if output_schema_strict is not None:
            additional_config["output_schema_strict"] = output_schema_strict
        if output_type:
            additional_config["output_type"] = output_type
        if tools:
            additional_config["tools"] = tools
        if handoffs:
            additional_config["handoffs"] = [
                handoff(h.agent, on_handoff=self._on_handoff_call) for h in handoffs
            ]

        self._agent = Agent(
            name=name, instructions=instructions, model="gpt-4o", **additional_config
        )

    @property
    def agent(self):
        return self._agent

    def _on_handoff_call(self, *args):
        logger.info("agent_service_on_handoff_call", message=args)

    async def run(self, input: str | None = None):
        if not input:
            raise OpenAIAgentEmptyUserInputException()

        try:
            result = await Runner.run(
                self._agent,
                input,
            )
            return result
        except Exception as e:
            logger.warning("openai_llm_agent_service", message=str(e))
            raise OpenAIAgentRuntimeException()
