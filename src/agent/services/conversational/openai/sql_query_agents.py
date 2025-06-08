from django.conf import settings
from openai import OpenAI
from pydantic import BaseModel

SQL_QUERY_PROMPT = """
# Context
You are a data analyst. Your job is to assist users who are looking for job opportunities from the data contained in a PostgreSQL database.

## Database Schema

### Job Opportunities Table
**Description:** Stores job opportunities for potential candidates.

                        Table "public.job_opportunities"
       Column        |           Type           | Collation | Nullable | Default
---------------------+--------------------------+-----------+----------+---------
 created_at          | timestamp with time zone |           | not null |
 updated_at          | timestamp with time zone |           | not null |
 id                  | uuid                     |           | not null |
 title               | character varying(60)    |           | not null |
 years_of_experience | character varying(3)     |           | not null |
 location            | character varying(60)    |           | not null |
 skills              | character varying(100)[] |           | not null |
 salary              | integer                  |           | not null |
Indexes:
    "job_opportunities_pkey" PRIMARY KEY, btree (id)


# Instructions:
1. When the user asks a question searching for job opportunities with certain parameters like for
example "Patent attorney with 7 years of experience in Patrickfort", consider what data you would need to answer
the question and confirm that the data should be available by consulting the database schema.
2. Use a clause ILIKE in the WHERE conditions for all fields.

# User's search
{user_search}
"""


class JobSearchQuery(BaseModel):
    query: str


client = OpenAI(api_key=settings.OPENAPI_API_KEY)


def generate_query(user_search: str):
    response = client.responses.parse(
        model="gpt-4.1",
        input=user_search,
        text_format=JobSearchQuery,
    )
    return response
