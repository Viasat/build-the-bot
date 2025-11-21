import pytest
from unittest.mock import patch, MagicMock
from build_the_bot.nlp.chat_gpt import ChatGPT


class TestChatGPTInit:
    def test_initialization_creates_client(self):
        with patch("build_the_bot.nlp.chat_gpt.AzureOpenAI") as mock_azure:
            mock_client = MagicMock()
            mock_azure.return_value = mock_client

            chatgpt = ChatGPT(
                api_key="test_key",
                deployment_name="test_deployment",
                api_version="2023-05-15",
                endpoint="https://test.openai.azure.com/",
            )

            assert chatgpt.deployment_name == "test_deployment"
            assert chatgpt.client == mock_client
            mock_azure.assert_called_once_with(
                api_key="test_key",
                api_version="2023-05-15",
                azure_endpoint="https://test.openai.azure.com/",
            )


@pytest.fixture()
def chat_response():
    def mock_chat_response(content):
        mock_message = MagicMock()
        mock_message.content = content
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        return mock_client

    return mock_chat_response


class TestRunRecognition:
    @patch("build_the_bot.nlp.chat_gpt.AzureOpenAI")
    def test_run_recognition_basic_call(self, mock_azure, chat_response):
        mock_client = chat_response("greeting")
        mock_azure.return_value = mock_client

        chatgpt = ChatGPT(
            api_key="test_key",
            deployment_name="test_deployment",
            api_version="2023-05-15",
            endpoint="https://test.openai.azure.com/",
        )
        prompt = "Identify the intent of this message."
        user_message_sent = "Hello there"
        result = chatgpt.run_recognition(
            user_message=user_message_sent,
            prompt=prompt,
        )
        expected_messages = [{"role": "system", "content": prompt}, {"role": "user", "content": user_message_sent}]

        assert result == "greeting"
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs["model"] == "test_deployment"
        assert call_args.kwargs["max_completion_tokens"] == 50
        assert call_args.kwargs["messages"] == expected_messages

    @patch("build_the_bot.nlp.chat_gpt.AzureOpenAI")
    def test_run_recognition_with_fsl_data(self, mock_azure, chat_response):
        mock_client = chat_response("dev")
        mock_azure.return_value = mock_client

        chatgpt = ChatGPT(
            api_key="test_key",
            deployment_name="test_deployment",
            api_version="2023-05-15",
            endpoint="https://test.openai.azure.com/",
        )

        fsl_data = [
            {"role": "user", "content": "run on staging"},
            {"role": "assistant", "content": "staging"},
            {"role": "user", "content": "deploy to prod"},
            {"role": "assistant", "content": "prod"},
        ]
        prompt = "Extract the server name."
        user_message_sent = "run on dev"
        result = chatgpt.run_recognition(
            user_message=user_message_sent,
            prompt=prompt,
            fsl_data=fsl_data,
        )

        expected_messages = [{"role": "system", "content": prompt}]
        expected_messages.extend(fsl_data)
        expected_messages.append({"role": "user", "content": user_message_sent})

        assert result == "dev"
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs["messages"] == expected_messages

    @patch("build_the_bot.nlp.chat_gpt.AzureOpenAI")
    def test_run_recognition_custom_max_tokens(self, mock_azure, chat_response):
        mock_client = chat_response("response")
        mock_azure.return_value = mock_client

        chatgpt = ChatGPT(
            api_key="test_key",
            deployment_name="test_deployment",
            api_version="2023-05-15",
            endpoint="https://test.openai.azure.com/",
        )

        result = chatgpt.run_recognition(
            user_message="Test message",
            prompt="Test prompt",
            max_returned_tokens=200,
        )

        assert result == "response"
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs["max_completion_tokens"] == 200
