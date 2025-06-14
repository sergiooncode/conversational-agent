# Generated by Django 5.2 on 2025-06-06 15:10

import django.contrib.postgres.fields
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="JobOpportunity",
            fields=[
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("title", models.CharField(max_length=60)),
                ("years_of_experience", models.CharField(max_length=3)),
                ("location", models.CharField(max_length=60)),
                (
                    "skills",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=100), size=None
                    ),
                ),
                ("salary", models.IntegerField()),
            ],
            options={
                "db_table": "job_opportunities",
            },
        ),
    ]
