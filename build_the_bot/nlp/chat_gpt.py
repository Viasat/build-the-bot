"""
Definition of the ChatGPT class.
"""

from openai import AzureOpenAI


class ChatGPT:
    """
    A ChatGPT wrapper to assist with intent disambiguation and entity recognition.
    """

    def __init__(
        self,
        api_key,
        deployment_name,
        api_version,
        endpoint,
    ):
        self.deployment_name = deployment_name
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint,
        )

    def run_recognition(self, user_message, prompt, fsl_data=None, max_returned_tokens=50):
        """
        Combines the prompt, few shot data, if any, and the user message to recognize an intent or entity.
        :param str user_message: the message from the user
        :param str prompt: the system prompt to use
        :param List(Dict(str, str)) fsl_data: A list of dictionaries representing a conversation
            in the following format:
            [{"role":"user", "content": "example message"}, {"role":"assistant":"example response"}]
        :param int max_returned_tokens: The maximum number of tokens ChatGPT can generate in its response
        :return str: ChatGPT's response message
        """
        messages = [
            {"role": "system", "content": prompt},
        ]
        if fsl_data:
            messages.extend(fsl_data)
        messages.append({"role": "user", "content": user_message})
        response = self.client.chat.completions.create(
            model=self.deployment_name, messages=messages, max_completion_tokens=max_returned_tokens
        )
        return response.choices[0].message.content
