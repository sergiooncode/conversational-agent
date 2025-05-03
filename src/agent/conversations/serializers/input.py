from enum import Enum

from rest_framework import serializers
from rest_framework import fields


class ConversationBotFunction(Enum):
    CUSTOMER_SUPPORT = "customer_support"


class ConversationCreateInputSerializer(serializers.Serializer):
    function = fields.ChoiceField(
        choices=[f.value for f in list(ConversationBotFunction)],
        default=ConversationBotFunction.CUSTOMER_SUPPORT.value,
    )


class ConversationPartialUpdateInputSerializer(serializers.Serializer):
    message = fields.CharField(required=True)
