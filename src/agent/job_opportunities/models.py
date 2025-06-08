import uuid

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex

from agent.common.models import BaseModel


class JobOpportunity(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=60, null=False, blank=False)
    years_of_experience = models.CharField(max_length=3, null=False, blank=False)
    location = models.CharField(max_length=60, null=False, blank=False)
    skills = ArrayField(
        models.CharField(max_length=100), null=False, blank=False, default=list
    )
    salary = models.IntegerField(null=False, blank=False)

    class Meta:
        db_table = "job_opportunities"
        indexes = [
            GinIndex(fields=["skills"], name="skills_idx"),
            GinIndex(fields=["title"], name="title_idx"),
            GinIndex(fields=["location"], name="location_idx"),
        ]
