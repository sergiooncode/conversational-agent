import uuid

from django.core.management import BaseCommand, CommandParser

from agent.conversations.models import Conversation
from agent.services.text_to_speech.eleven_labs.service import TextToSpeechService


class Command(BaseCommand):
    help = "Create a speech from text for a conversation"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--conversation_id",
            required=True,
            help="Id of the conversation which should have a summary so "
            "a speech can be generated for it to be used by an agent "
            "on a follow up call",
        )

    def handle(self, *args, **options) -> str | None:
        conversation_id = options.get("conversation_id")
        try:
            uuid.UUID(conversation_id)
        except Exception:
            exit(1)
        conversation = None
        try:
            conversation = Conversation.objects.get(pk=conversation_id)
        except Exception as e:
            print(e)
            exit(1)

        print(conversation)

        service = TextToSpeechService()
        service.convert_and_save_to_file(
            text="I'm calling from the Customer Support of the fictional business "
            "regarding the order number"
        )
