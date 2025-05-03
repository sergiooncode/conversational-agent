from rest_framework import serializers

from agent.conversations.models import Conversation


class ConversationCreateOutputSerializer(serializers.ModelSerializer):
    conversation_id = serializers.CharField(source="id")
    bot_id = serializers.CharField(source="bot.id")
    human_user_id = serializers.CharField(source="human_user.id")

    class Meta:
        model = Conversation
        fields = ["conversation_id", "bot_id", "human_user_id"]


class ConversationPartialUpdateOutputSerializer(serializers.Serializer):
    bot_message = serializers.CharField(required=True)
