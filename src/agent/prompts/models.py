import uuid

from django.db import models

from agent.bots.models import BotFunction
from agent.common.models import BaseModel


BOT_FUNCTION_TO_PROMPT_MAP = {
    BotFunction.CUSTOMER_SUPPORT.value: {
        0: {
            "name": "Customer Support Inquirer",
            "instructions": (
                "The customer has a problem so, using a corteous and pleasant "
                "tone since the customer can be frustrated, determine from the "
                "customer the following information: order number, problem "
                "category, problem description, and urgency level. Once the customer "
                "has provided all the information delegate the customer accordingly. "
                "If the user has provided all the information, "
                "handoff to the Customer Support Closer agent."
            ),
        },
        1: {
            "name": "Customer Support Closer",
            "instructions": (
                "When you enter into the picture the customer already provided the information "
                "to handle the issue so close the conversation with the customer reassuring that "
                "everything possible will be done to solve their issue and keep the customer updated "
                "during the whole resolution process."
            ),
        },
    }
}


class Prompt(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField(null=False)
    function = models.CharField(
        max_length=20, choices=BotFunction.choices, default=BotFunction.CUSTOMER_SUPPORT
    )

    class Meta:
        db_table = "prompts"
