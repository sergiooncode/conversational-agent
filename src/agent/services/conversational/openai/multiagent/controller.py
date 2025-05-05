from agents import Agent, Runner

from agent.bots.models import BotFunction
from agent.prompts.models import BOT_FUNCTION_TO_PROMPT_MAP
from agent.services.conversational.openai.agents import (
    AgentService,
    CollectedInfo,
    collected_information,
)

cs_agent_service_2 = AgentService(
    name=BOT_FUNCTION_TO_PROMPT_MAP[BotFunction.CUSTOMER_SUPPORT.value][2]["name"],
    instructions=BOT_FUNCTION_TO_PROMPT_MAP[BotFunction.CUSTOMER_SUPPORT.value][2][
        "instructions"
    ],
)

cs_agent_service_1 = AgentService(
    name=BOT_FUNCTION_TO_PROMPT_MAP[BotFunction.CUSTOMER_SUPPORT.value][1]["name"],
    instructions=BOT_FUNCTION_TO_PROMPT_MAP[BotFunction.CUSTOMER_SUPPORT.value][1][
        "instructions"
    ],
    tools=[collected_information],
    output_type=CollectedInfo,
    handoffs=[cs_agent_service_2],
)

cs_agent_service_0 = AgentService(
    name=BOT_FUNCTION_TO_PROMPT_MAP[BotFunction.CUSTOMER_SUPPORT.value][0]["name"],
    instructions=BOT_FUNCTION_TO_PROMPT_MAP[BotFunction.CUSTOMER_SUPPORT.value][0][
        "instructions"
    ],
    handoffs=[cs_agent_service_1],
)


CUSTOMER_SUPPORT_AGENT_MAP = {
    "triaging_and_info_collector": cs_agent_service_0,
    "info_structurer": cs_agent_service_1,
    "user_reassurance_and_send_off": cs_agent_service_2,
}


class MultiAgentController:
    def __init__(self, agent_map=CUSTOMER_SUPPORT_AGENT_MAP):
        self.agents = agent_map

    def run(self, agent_name, history=None):
        """
        Run an agent by name, pass message and optional history.
        Returns result and agent name.
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} not found.")

        # Run agent
        result = Runner.run(self.agents[agent_name], input=history)

        return result.final_output

    def route(self, message, history=None):
        """
        Main router logic → decide which agent to run first
        """

        msg_lower = message.lower()

        if (
            "order number" in msg_lower
            or "problem" in msg_lower
            or "urgency" in msg_lower
        ):
            agent = "info_structurer"
        elif "follow up" in msg_lower or "asap" in msg_lower:
            agent = "user_reassurance_and_send_off"
        else:
            agent = "triaging_and_info_collector"

        # Run chosen agent
        response = self.run(agent, message, history)

        return agent, response
