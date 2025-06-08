import json
import time

import structlog
from django.core.management.base import BaseCommand
from django.db import connection

from agent.services.conversational.openai.sql_query_agents import (
    SQL_QUERY_PROMPT,
    generate_query,
)

logger = structlog.get_logger(__name__)


class Command(BaseCommand):
    help = "Generate test job data"

    def add_arguments(self, parser):
        parser.add_argument("--user_search", type=str)

    def handle(self, *args, **kwargs):
        user_search = kwargs["user_search"]
        time_start = time.perf_counter()
        text_result = (
            generate_query(f"{SQL_QUERY_PROMPT}{user_search}").output[0].content[0].text
        )
        result = json.loads(text_result)
        query = result["query"]
        print(query)
        with connection.cursor() as cursor:
            cursor.execute(query)
            print(cursor.fetchall())
        time_elapsed = time.perf_counter() - time_start
        logger.info("time_elapsed", time_start=time_start, time_elapsed=time_elapsed)
