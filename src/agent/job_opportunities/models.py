import uuid

from django.db import models

from agent.common.models import BaseModel


class JobOpportunity(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = function = models.CharField(max_length=20, null=False, blank=False)

    class Meta:
        db_table = "job_opportunities"
