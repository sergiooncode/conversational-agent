import asyncio
from unittest import mock
from unittest.mock import MagicMock

import pytest
from django.test.utils import override_settings

from agent.services.exceptions import (
    OpenAIAgentNotConfiguredException,
    OpenAIAgentEmptyUserInputException,
)
from agent.services.llm.openai.agents import AgentService


def async_return(result):
    f = asyncio.Future()
    f.set_result(result)
    return f


class TestOpenAIAgentService:
    @override_settings(OPENAPI_API_KEY="key")
    def test_agent_configured_successfully(self):
        with mock.patch(
            "agent.services.llm.openai.agents.Agent"
        ) as agent_mock_class, mock.patch(
            "agent.services.llm.openai.agents.handoff"
        ) as handoff_mock:
            mock_tool = MagicMock()
            mock_output_type = MagicMock()
            mock_handoff_function = MagicMock()
            AgentService(
                name="Customer Support Agent",
                instructions="Some instructions",
                tools=[mock_tool],
                output_type=mock_output_type,
                handoffs=[mock_handoff_function],
            )
            agent_mock_class.assert_called_with(
                name="Customer Support Agent",
                instructions="Some instructions",
                model="gpt-4o",
                tools=[mock_tool],
                output_type=mock_output_type,
                handoffs=[handoff_mock(mock_handoff_function)],
            )

    @override_settings(OPENAPI_API_KEY="key")
    def test_agent_not_configured_when_missing_fields(self):
        with pytest.raises(OpenAIAgentNotConfiguredException):
            AgentService()

    @pytest.mark.asyncio
    @override_settings(OPENAPI_API_KEY="key")
    @pytest.mark.parametrize("input", [None, ""])
    async def test_agent_raises_when_run_with_no_user_input(self, input):
        with pytest.raises(OpenAIAgentEmptyUserInputException):
            agent = AgentService(
                name="Customer Support Agent",
                instructions="Some instructions",
            )
            await agent.run(input)

    @pytest.mark.asyncio
    @override_settings(OPENAPI_API_KEY="key")
    async def test_agent_returns_result_when_received_user_input(self):
        with mock.patch(
            "agent.services.llm.openai.agents.Agent"
        ), mock.patch(
            "agent.services.llm.openai.agents.Runner"
        ) as runner_mock_class:
            mock_result = "Agent: how can i help?"
            runner_mock_class.run.return_value = async_return(mock_result)
            agent = AgentService(
                name="Customer Support Agent",
                instructions="Some instructions",
            )
            actual_result = await agent.run(
                input="User: i have an issue\nAssistant: how can i help?\n")

            assert actual_result == mock_result
