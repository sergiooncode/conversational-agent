from django.core.management.base import BaseCommand
from myapp.models import Job
from faker import Faker
import random


class Command(BaseCommand):
    help = "Generate test job data"

    def add_arguments(self, parser):
        parser.add_argument("--total", type=int, default=100000)

    def handle(self, *args, **kwargs):
        total = kwargs["total"]
        fake = Faker()

        jobs = []
        for _ in range(total):
            jobs.append(
                Job(
                    title=fake.job(),
                    location=fake.city(),
                    salary=random.randint(40000, 200000),
                    remote=random.choice([True, False]),
                    skills=", ".join(fake.words(nb=3, unique=True)),
                )
            )

            # Use batch insertion for performance
            if len(jobs) >= 10000:
                Job.objects.bulk_create(jobs, batch_size=1000)
                jobs.clear()

        # Insert remaining records
        if jobs:
            Job.objects.bulk_create(jobs, batch_size=1000)

        self.stdout.write(self.style.SUCCESS(f"Generated {total} job entries."))
