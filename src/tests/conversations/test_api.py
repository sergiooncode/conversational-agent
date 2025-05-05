from unittest import mock
from unittest.mock import ANY, MagicMock

import pytest

from tests.conftest import async_return

pytestmark = pytest.mark.django_db


class TestConversationsCreateViewSet:
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

    def test_create_conversation_returns_500_when_creation_manager_raises_exception(
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


class TestConversationsPartialUpdateViewSet:
    base_endpoint = "/api/conversations/"

    def test_partial_update_conversation_successfully(
        self, api_client, valid_bot_message
    ):
        with mock.patch(
            "agent.conversations.views.ConversationPartialUpdateManager"
        ) as manager_mock:
            manager_mock_instance = MagicMock()
            manager_mock_instance.partial_update.return_value = async_return(
                valid_bot_message
            )
            manager_mock.return_value = manager_mock_instance
            response = api_client.patch(
                path=f"{self.base_endpoint}16b6353d-f3ff-4abe-8b17-c4dd596171f9/",
                data={"message": "i have an issue"},
                formt="json",
            )

        assert response.status_code == 200
        assert response.json() == {"bot_message": valid_bot_message}

    def test_partial_update_conversation_returns_400_when_no_message(
        self, api_client, valid_bot_message
    ):
        with mock.patch(
            "agent.conversations.views.ConversationPartialUpdateManager"
        ) as manager_mock:
            manager_mock_instance = MagicMock()
            manager_mock_instance.partial_update.return_value = async_return(
                valid_bot_message
            )
            manager_mock.return_value = manager_mock_instance
            response = api_client.patch(
                path=f"{self.base_endpoint}16b6353d-f3ff-4abe-8b17-c4dd596171f9/",
                data={},
                formt="json",
            )

        assert response.status_code == 400
        assert response.json() == {"message": ["This field is required."]}

    def test_partial_update_conversation_returns_404_when_conversation_not_found(
        self, api_client, valid_bot_message
    ):
        with mock.patch(
            "agent.conversations.managers.partial_update.AgentService"
        ) as agent_service_mock:
            agent_service_mock.run.return_value = async_return(valid_bot_message)
            response = api_client.patch(
                path=f"{self.base_endpoint}16b6353d-f3ff-4abe-8b17-c4dd596171f9/",
                data={"message": "i have an issue"},
                formt="json",
            )

        assert response.status_code == 404
        assert response.json() == {"detail": "Conversation not found"}

    def test_partial_update_conversation_returns_500_when_creation_manager_raises_exception(
        self, api_client, valid_bot_message
    ):
        with mock.patch(
            "agent.conversations.views.ConversationPartialUpdateManager"
        ) as manager_mock:
            manager_mock_instance = MagicMock()
            manager_mock_instance.partial_update.side_effect = async_return(Exception())
            manager_mock.return_value = manager_mock_instance
            response = api_client.patch(
                path=f"{self.base_endpoint}16b6353d-f3ff-4abe-8b17-c4dd596171f9/",
                data={"message": "i have an issue"},
                formt="json",
            )

        assert response.status_code == 500
        assert response.json() == {"detail": "A server error occurred."}


class TestConversationCreateFollowupSpeechViewSet:
    base_endpoint = "/api/conversations/"

    def test_create_conversation_followup_speech_successfully(
        self, api_client, valid_bot_message
    ):
        with mock.patch(
            "agent.conversations.views.ConversationCreateFollowupSpeechManager"
        ) as manager_mock:
            manager_mock_instance = MagicMock()
            manager_mock_instance.create.return_value = (
                "daa314c2-3723-4b63-afff-a5430616416a.mp3"
            )
            manager_mock.return_value = manager_mock_instance
            response = api_client.post(
                path=f"{self.base_endpoint}16b6353d-f3ff-4abe-8b17-c4dd596171f9/follow-up-speech/"
            )

        assert response.status_code == 201
        assert response.json() == {
            "speech_id": "daa314c2-3723-4b63-afff-a5430616416a.mp3"
        }
