import uuid

from django.db import models

from agent.common.models import BaseModel


class Conversation(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    raw_conversation = models.JSONField(default=list, null=True)
    summary = models.JSONField(default=dict, null=True)
    human_user = models.ForeignKey(
        "human_users.HumanUser",
        null=True,
        related_name="human_users",
        on_delete=models.PROTECT,
    )
    bot = models.ForeignKey(
        "bots.Bot", null=True, related_name="bots", on_delete=models.PROTECT
    )

    class Meta:
        db_table = "conversations"
