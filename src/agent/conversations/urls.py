from django.urls import path

from agent.conversations.views import (
    ConversationCreateFollowupSpeechViewSet,
    ConversationViewSet,
)

urlpatterns = [
    path(
        "conversations/",
        ConversationViewSet.as_view({"post": "post"}),
        name="conversations_create",
    ),
    path(
        "conversations/<uuid:pk>/",
        ConversationViewSet.as_view({"patch": "partial_update"}),
        name="conversations_partial_update",
    ),
    path(
        "conversations/<uuid:pk>/follow-up-speech/",
        ConversationCreateFollowupSpeechViewSet.as_view({"post": "post"}),
        name="conversations_followupspeech_create",
    ),
]
