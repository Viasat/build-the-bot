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


class TestRunRecognition:
    @patch("build_the_bot.nlp.chat_gpt.AzureOpenAI")
    def test_run_recognition_basic_call(self, mock_azure):
        # Mock the response structure
        mock_message = MagicMock()
        mock_message.content = "greeting"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure.return_value = mock_client

        chatgpt = ChatGPT(
            api_key="test_key",
            deployment_name="test_deployment",
            api_version="2023-05-15",
            endpoint="https://test.openai.azure.com/",
        )

        result = chatgpt.run_recognition(
            user_message="Hello there",
            prompt="Identify the intent of this message.",
        )

        assert result == "greeting"
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs["model"] == "test_deployment"
        assert call_args.kwargs["max_completion_tokens"] == 50
        assert len(call_args.kwargs["messages"]) == 2
        assert call_args.kwargs["messages"][0]["role"] == "system"
        assert call_args.kwargs["messages"][0]["content"] == "Identify the intent of this message."
        assert call_args.kwargs["messages"][1]["role"] == "user"
        assert call_args.kwargs["messages"][1]["content"] == "Hello there"

    @patch("build_the_bot.nlp.chat_gpt.AzureOpenAI")
    def test_run_recognition_with_fsl_data(self, mock_azure):
        mock_message = MagicMock()
        mock_message.content = "dev"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
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

        result = chatgpt.run_recognition(
            user_message="run on dev",
            prompt="Extract the server name.",
            fsl_data=fsl_data,
        )

        assert result == "dev"
        call_args = mock_client.chat.completions.create.call_args
        assert len(call_args.kwargs["messages"]) == 6  # system + 4 fsl + user
        assert call_args.kwargs["messages"][0]["role"] == "system"
        assert call_args.kwargs["messages"][1] == fsl_data[0]
        assert call_args.kwargs["messages"][2] == fsl_data[1]
        assert call_args.kwargs["messages"][3] == fsl_data[2]
        assert call_args.kwargs["messages"][4] == fsl_data[3]
        assert call_args.kwargs["messages"][5]["role"] == "user"
        assert call_args.kwargs["messages"][5]["content"] == "run on dev"

    @patch("build_the_bot.nlp.chat_gpt.AzureOpenAI")
    def test_run_recognition_custom_max_tokens(self, mock_azure):
        mock_message = MagicMock()
        mock_message.content = "response"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
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

   