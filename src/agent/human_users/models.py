import uuid

from django.db import models

from agent.common.models import BaseModel


class HumanUser(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        db_table = "human_users"
