from django.urls import include, path
from rest_framework import routers
from django.contrib import admin

from agent.conversations.views import ConversationViewSet

router = routers.DefaultRouter()

router.register(r"conversations", ConversationViewSet, basename="conversations")

urlpatterns = [
    path("", include("agent.conversations.urls")),
    path("api/", include("agent.conversations.urls")),
    path("admin/", admin.site.urls),
]
