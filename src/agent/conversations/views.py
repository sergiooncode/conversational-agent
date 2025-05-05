from uuid import UUID

import structlog
from adrf import viewsets
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import APIException, NotFound, NotAuthenticated

from agent.conversations.exceptions import (
    ConversationNotFound,
    ConversationSummaryDoesntExist,
)
from agent.conversations.managers.creation import (
    ConversationCreationManager,
    ConversationCreateFollowupSpeechManager,
)
from agent.conversations.managers.partial_update import ConversationPartialUpdateManager
from agent.conversations.serializers.input import (
    ConversationCreateInputSerializer,
    ConversationPartialUpdateInputSerializer,
)
from agent.conversations.serializers.output import (
    ConversationCreateOutputSerializer,
    ConversationPartialUpdateOutputSerializer,
)
from agent.services.exceptions import OpenAIAPIkeyNotConfigured

logger = structlog.get_logger(__name__)


class ConversationViewSet(viewsets.ViewSet):
    def post(self, request: Request, *args, **kwargs):
        input_serializer = ConversationCreateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        validated_data = input_serializer.validated_data

        try:
            conversation = ConversationCreationManager(context=validated_data).create()
        except Exception as e:
            logger.error("conversation_view_post", message=e)
            raise APIException()

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
        except ConversationNotFound as e:
            logger.warning("conversation_view_partial_update_not_found", message=e)
            raise NotFound(
                detail="Conversation not found",
            )
        except OpenAIAPIkeyNotConfigured as e:
            raise NotAuthenticated(detail=e.message)
        except Exception as e:
            logger.error("conversation_view_partial_update", message=e)
            raise APIException()

        output_serializer = ConversationPartialUpdateOutputSerializer(
            data={"bot_message": bot_message}
        )
        output_serializer.is_valid(raise_exception=False)
        validated_data = output_serializer.validated_data

        return Response(data=validated_data, status=status.HTTP_200_OK)


class ConversationCreateFollowupSpeechViewSet(viewsets.ViewSet):
    def post(self, request: Request, pk: UUID, *args, **kwargs):
        try:
            speech_recording_id = ConversationCreateFollowupSpeechManager().create(
                conversation_id=pk
            )
        except ConversationNotFound as e:
            logger.warning(
                "conversation_view_post_followup_speech_not_found", message=e
            )
            raise NotFound(
                detail="Conversation not found",
            )
        except ConversationSummaryDoesntExist as e:
            logger.warning(
                "conversation_view_post_followup_speech_summary_not_found", message=e
            )
            raise NotFound(
                detail="Conversation summary not found",
            )
        except Exception as e:
            import traceback;traceback.print_exc()
            logger.error("conversation_view_post_followup_speech_post", message=e)
            raise APIException()

        return Response(
            data={"speech_id": speech_recording_id}, status=status.HTTP_201_CREATED
        )
