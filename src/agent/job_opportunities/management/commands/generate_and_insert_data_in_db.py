import random

import structlog
from django.core.management.base import BaseCommand
from faker import Faker

from agent.job_opportunities.models import JobOpportunity

SKILLS = [
    "Python",
    "Django",
    "React",
    "SQL",
    "AWS",
    "Docker",
    "Kubernetes",
    "TensorFlow",
    "PyTorch",
    "Git",
    "PostgreSQL",
    "REST APIs",
    "Mental health assessment",
    "Patient crisis intervention",
    "Medication administration and monitoring",
    "Pattern and print development",
    "CAD software (e.g., Adobe Illustrator, NedGraphics)",
    "Knowledge of fabric construction and color theory",
    "Fermentation science and microbiology",
    "Quality control and lab testing",
    "Brewery process automation and equipment handling",
    "Statistical and data analysis (e.g., R, Python, Excel)",
    "Risk modeling and scenario planning",
    "Knowledge of regulatory frameworks (e.g., Basel II/III, SOX)",
    "Facility operations and maintenance",
    "Guest service and conflict resolution",
    "Staff scheduling and training",
    "Surface pattern design",
    "Trend forecasting",
    "Fabric dyeing and printing techniques",
    "Financial reporting and auditing",
    "Tax compliance and planning",
    "Use of accounting software (e.g., SAP, QuickBooks)",
    "Software development (e.g., Python, Java, JavaScript)",
    "Database management (e.g., PostgreSQL, MongoDB)",
    "Version control (e.g., Git)",
    "Technical product knowledge",
    "Client relationship management",
    "Solution-based selling and demos",
]

logger = structlog.get_logger(__name__)


class Command(BaseCommand):
    help = "Generate test job data"

    def add_arguments(self, parser):
        parser.add_argument("--total", type=str)

    def handle(self, *args, **kwargs):
        total = kwargs["total"]
        fake = Faker()

        jobs = []
        for counter in range(total):
            params = dict(
                title=fake.job(),
                location=fake.city(),
                salary=random.randint(40000, 200000),
                years_of_experience=str(random.randint(1, 10)),
                skills=random.sample(SKILLS, k=random.randint(2, 4)),
            )

            jobs.append(JobOpportunity(**params))

            # Use batch insertion for performance
            if len(jobs) >= 10000:
                JobOpportunity.objects.bulk_create(jobs, batch_size=10000)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Inserted {len(jobs)} " f"job entries, progress at {counter}."
                    )
                )
                jobs.clear()

        # Insert remaining records
        if jobs:
            JobOpportunity.objects.bulk_create(jobs, batch_size=10000)

        self.stdout.write(self.style.SUCCESS(f"Generated {total} job entries."))
