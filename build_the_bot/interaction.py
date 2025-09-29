"""
Classes that define interactions with messaging platforms.
"""

from abc import ABC, abstractmethod
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.models.blocks import ActionsBlock, ButtonElement, SectionBlock, PlainTextObject


# an abstract class
class Interaction(ABC):
    """
    An abstract class for messaging platform interaction.
    """

    # Abstract method, must be implemented by subclasses
    @abstractmethod
    async def send_message(self, message, channel_id, thread_id=None):
        """
        Send a message
        :param str message: text message to send
        :param str channel_id: uuid of the channel to send the message to.
        :param str thread_id: uuid of the thread the user is interacting from.
            None, if messaging without a thread (dms).
        """
        pass  # pragma: no cover


# Concrete subclass of Interaction
class SlackInteraction(Interaction):

    def __init__(self, client: AsyncWebClient):
        """
        Initialize a SlackInteraction object
        :param AsyncWebClient client: Slack web client
        """
        self.client = client

    async def send_message(self, message, channel_id, thread_id=None):
        """
        Send a message
        :param str message: text message to send
        :param str channel_id: Slack uuid of the channel to send the message to
        :param str thread_id: Slack uuid of the thread the user is interacting from.
            None, if messaging without a thread (dms).
        """
        await self.client.chat_postMessage(channel=channel_id, text=message, thread_ts=thread_id)

    async def send_large_code_message(self, message, channel_id, thread_id=None):
        """
        Send a large message in formatted as code
        :param str message: text message to send
        :param str channel_id: Slack uuid of the channel to send the message to
        :param str thread_id: Slack uuid of the thread the user is interacting from.
            None, if messaging without a thread (dms).
        """
        max_char = 4000
        init_value = 0
        messages_to_send = len(message) // max_char
        if messages_to_send > 0:
            for i in range(messages_to_send):
                await self.client.chat_postMessage(
                    text="```" + message[init_value : (((i + 1) * max_char) - 1)] + "```",
                    channel=channel_id,
                    thread_ts=thread_id,
                )
                init_value = (i + 1) * max_char
            if init_value < len(message):
                await self.client.chat_postMessage(
                    text="```" + message[init_value : len(message)] + "```", channel=channel_id, thread_ts=thread_id
                )
        else:
            await self.client.chat_postMessage(text="```" + message + "```", channel=channel_id, thread_ts=thread_id)

    async def send_buttons(self, title, buttons: dict, channel_id, thread_id=None, emoji=False):
        """
        Send a message with buttons
        :param str title: Message to send with the buttons
        :param Dict(str, str) buttons: Dictionary mapping the text on each button to the Slack action event name
        :param str channel_id: Slack uuid of the channel to send the message to
        :param str thread_id: Slack uuid of the thread the user is interacting from.
            None, if messaging without a thread (dms).
        :param boolean emoji: Whether emojis should be escaped into the colon emoji format in Slack elements.
        """
        button_elements = []
        for name, action in buttons.items():
            button_elements.append(ButtonElement(text=PlainTextObject(text=name, emoji=emoji), action_id=action))
        await self.client.chat_postMessage(
            text=title,
            channel=channel_id,
            blocks=[
                SectionBlock(text=PlainTextObject(text=title, emoji=emoji)),
                ActionsBlock(elements=button_elements),
            ],
            thread_ts=thread_id,
        )
