from django.contrib import admin

from agent.conversations.models import Conversation


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["created_at", "raw_conversation", "summary", "human_user", "bot"]
    ordering = ("-created_at",)
