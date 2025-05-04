from unittest import mock
from unittest.mock import ANY, MagicMock

import pytest

pytestmark = pytest.mark.django_db


class TestConversationsViewSet:
    base_endpoint = "/api/conversations/"

    def test_create_conversation_successfully(self, api_client):
        response = api_client.post(
            path=self.base_endpoint, data={"function": "customer_support"}, formt="json"
        )

        assert response.status_code == 201
        assert response.json() == {
            "bot_id": ANY,
            "human_user_id": ANY,
            "conversation_id": ANY,
        }

    def test_create_conversation_returns_400_with_invalid_function(self, api_client):
        response = api_client.post(
            path=self.base_endpoint, data={"function": "invalid_function"}, formt="json"
        )

        assert response.status_code == 400
        assert response.json() == {
            "function": [
                '"invalid_function" is not a valid choice.',
            ]
        }

    def test_create_conversation_returns_500_when_creation_manager_raises(
        self, api_client
    ):
        with mock.patch(
            "agent.conversations.views.ConversationCreationManager"
        ) as manager_mock:
            manager_mock_instance = MagicMock()
            manager_mock_instance.create.side_effect = Exception()
            manager_mock.return_value = manager_mock_instance
            response = api_client.post(
                path=self.base_endpoint,
                data={"function": "customer_support"},
                formt="json",
            )

        assert response.status_code == 500
        assert response.json() == {"detail": "A server error occurred."}
