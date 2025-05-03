from django.urls import path

from agent.conversations.views import ConversationViewSet

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
]
