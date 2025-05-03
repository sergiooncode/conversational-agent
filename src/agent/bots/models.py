import uuid

from django.db import models

from agent.common.models import BaseModel
from agent.conversations.serializers.input import ConversationBotFunction


class BotFunction(models.TextChoices):
    CUSTOMER_SUPPORT = "CUSTOMER_SUPPORT", "Customer Support"


INPUTTED_FUNCTION_TO_BOT_FUNCTION_MAP = {
    ConversationBotFunction.CUSTOMER_SUPPORT.value: BotFunction.CUSTOMER_SUPPORT,
}


class Bot(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    function = models.CharField(
        max_length=20, choices=BotFunction.choices, default=BotFunction.CUSTOMER_SUPPORT
    )

    class Meta:
        db_table = "bots"
