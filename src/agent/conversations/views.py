from uuid import UUID

import structlog
from adrf import viewsets
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from agent.conversations.managers.creation import ConversationCreationManager
from agent.conversations.managers.partial_update import ConversationPartialUpdateManager
from agent.conversations.serializers.input import (
    ConversationCreateInputSerializer,
    ConversationPartialUpdateInputSerializer,
)
from agent.conversations.serializers.output import (
    ConversationCreateOutputSerializer,
    ConversationPartialUpdateOutputSerializer,
)

logger = structlog.get_logger(__name__)


class ConversationViewSet(viewsets.GenericViewSet):
    serializer_class = ConversationCreateOutputSerializer

    def post(self, request: Request, *args, **kwargs):
        input_serializer = ConversationCreateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        validated_data = input_serializer.validated_data

        try:
            conversation = ConversationCreationManager(context=validated_data).create()
        except Exception as e:
            logger.error("conversation_view", message=e)

        output_serializer = ConversationCreateOutputSerializer(instance=conversation)

        return Response(data=output_serializer.data, status=status.HTTP_201_CREATED)

    async def partial_update(self, request: Request, pk: UUID, *args, **kwargs):
        input_serializer = ConversationPartialUpdateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        validated_data = input_serializer.validated_data

        try:
            bot_message = await ConversationPartialUpdateManager(
                context=validated_data
            ).partial_update(conversation_id=pk)
        except Exception as e:
            logger.error("conversation_view", message=e)

        output_serializer = ConversationPartialUpdateOutputSerializer(
            data={"bot_message": bot_message}
        )
        output_serializer.is_valid(raise_exception=False)
        validated_data = output_serializer.validated_data

        return Response(data=validated_data, status=status.HTTP_200_OK)
