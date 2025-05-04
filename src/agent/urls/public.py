from django.urls import include, path
from rest_framework import routers
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from agent.conversations.views import ConversationViewSet

router = routers.DefaultRouter()

router.register(r"conversations", ConversationViewSet, basename="conversations")

urlpatterns = [
    path("", include("agent.conversations.urls")),
    path("api/", include("agent.conversations.urls")),
    path("admin/", admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
