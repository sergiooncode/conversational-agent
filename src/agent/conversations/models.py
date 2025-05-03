import uuid

from django.db import models

from agent.common.models import BaseModel


def default_summary():
    return dict(summary=[])


def default_raw_conversation():
    return dict(conversation=[])


class Conversation(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    raw_conversation = models.JSONField(default=default_raw_conversation, null=True)
    summary = models.JSONField(default=default_summary, null=True)
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
