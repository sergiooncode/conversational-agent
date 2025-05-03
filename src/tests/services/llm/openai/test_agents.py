from django.test.utils import override_settings

from agent.services.llm.openai.agents import AgentService


class TestOpenAIAgentService:

    @override_settings(OPENAPI_API_KEY="key")
    def test_agent_configured_and_started_successfully(self):
        agent = AgentService(
            name="Customer Support Agent", instructions="Some instructions"
        )
        agent.run(user_input="Some user input")

        assert 1 == 0
