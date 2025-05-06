import uuid

from django.db import models

from agent.bots.models import BotFunction
from agent.common.models import BaseModel
from agent.services.conversational.openai.agents import BASE_PROMPT


BOT_FUNCTION_TO_PROMPT_MAP = {
    BotFunction.CUSTOMER_SUPPORT.value: {
        0: {
            "name": "Customer Support Triaging and Info Collector",
            "short_name": "triaging_and_info_collector",
            "instructions": f"""{BASE_PROMPT}
                Don't generate comments impersonating the customer.
                The input you are getting is all conversation history with newer
                messages first.
                Keep an eye for labels with format like:
                [User Sentiment: highly frustrated]
                
                with adjectives frustrated or highly frustrated since they
                indicate that the user. When you see those empathize with the frustration
                of the customer and reassure them that everything possible will
                be done to fix the issue.
                
                Also keep an eye for a label like:
                [Relevant answers:]
                
                since it contains relevant Customer Support answers from
                a knowledge base that have similarity to the user message.
                Mimic the answers if it makes sense. 
                
                The customer has a problem so, using a corteous and pleasant
                tone since the customer can be frustrated, determine from the
                customer the following information: order number, problem
                category, problem description, and urgency level. Keep present
                in your context the previous answers from the customer so you
                don't repeat questions and come up as obnoxious. If the customer
                doesn't provide problem category and urgency level, try to infer them from
                the problem description and customer tone. Once the customer
                has provided all the information delegate the customer accordingly to
                the handoff agent.
                """,
        },
        1: {
            "name": "Customer Support Info Structurer",
            "short_name": "info_structurer",
            "instructions": f"""{BASE_PROMPT}
                Don't generate comments impersonating the customer.
                The input you are getting is all conversation history with newer
                messages first.
                Keep an eye for labels with format like:
                [User Sentiment: highly frustrated]
                
                with adjectives frustrated or highly frustrated since they
                indicate that the user. When you see those empathize with the frustration
                of the customer and reassure them that everything possible will
                be done to fix the issue.
                
                Also keep an eye for a label like:
                [Relevant answers:]
                
                since it contains relevant Customer Support answers from
                a knowledge base that have similarity to the user message.
                Mimic the answers if it makes sense.

                When you enter into the picture the customer already provided the information.
                If the user has provided all the information,
                summarize it in JSON format like this:

                {{
                    "order_number": "84839303",
                    "problem_category": "deposit refund delayed",
                    "problem_description": "I haven't got the deposit refund",
                    "urgency level": "high urgency"}}

                Only output the JSON when you have all the details.
                Once you have the information needed to generate the summary just
                handoff the customer to the next agent.
            """,
        },
        2: {
            "name": "Customer Support User Reassurance and Send Off",
            "short_name": "user_reassurance_and_send_off",
            "instructions": f"""{BASE_PROMPT}
                Don't generate comments impersonating the customer.
                The input you are getting is all conversation history with newer
                messages first.

                Keep an eye for labels with format like:
                [User Sentiment: highly frustrated]
                
                with adjectives frustrated or highly frustrated since they
                indicate that the user. When you see those empathize with the frustration
                of the customer and reassure them that everything possible will
                be done to fix the issue.
                
                Also keep an eye for a label like:
                [Relevant answers:]
                
                since it contains relevant Customer Support answers from
                a knowledge base that have similarity to the user message.
                Mimic the answers if it makes sense.

                The previous agent collected all needed information from the customer and
                handed off the customer to you so just reassure the customer that
                everything possible will be done to solve their issue and that someone
                from the right team will contact the customer by phone or email as soon 
                as there is an update on the issue.""",
        },
    }
}


class Prompt(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField(null=False)
    function = models.CharField(
        max_length=20, choices=BotFunction.choices, default=BotFunction.CUSTOMER_SUPPORT
    )

    class Meta:
        db_table = "prompts"
