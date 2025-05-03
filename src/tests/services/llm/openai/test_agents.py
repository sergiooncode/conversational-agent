from unittest import mock

import pytest
from django.test.utils import override_settings

from agent.services.exceptions import OpenAIAgentNotConfiguredException
from agent.services.llm.openai.agents import AgentService


class TestOpenAIAgentService:
    @override_settings(OPENAPI_API_KEY="key")
    def test_agent_configured_successfully(self):
        with mock.patch("agent.services.llm.openai.agents.Agent") as agent_mock_class:
            AgentService(
                name="Customer Support Agent", instructions="Some instructions"
            )
            agent_mock_class.assert_called_with(
                name="Customer Support Agent",
                instructions="Some instructions",
                model="gpt-4o",
            )

    @override_settings(OPENAPI_API_KEY="key")
    def test_agent_not_configured_when_missing_fields(self):
        with pytest.raises(OpenAIAgentNotConfiguredException):
            AgentService()
