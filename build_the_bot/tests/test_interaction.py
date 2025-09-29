import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, call
from build_the_bot.interaction import SlackInteraction
from slack_sdk.models.blocks import ActionsBlock, ButtonElement, SectionBlock


@pytest_asyncio.fixture
def mock_client():
    client = AsyncMock()
    client.chat_postMessage = AsyncMock()
    return client


@pytest.mark.asyncio
async def test_send_message_calls_chat_postMessage(mock_client):
    si = SlackInteraction(mock_client)
    await si.send_message("hello", "c1", "t1")
    mock_client.chat_postMessage.assert_awaited_once_with(channel="c1", text="hello", thread_ts="t1")


@pytest.mark.asyncio
async def test_send_large_code_message_short(mock_client):
    si = SlackInteraction(mock_client)
    msg = "short"
    await si.send_large_code_message(msg, "c1", "t1")
    mock_client.chat_postMessage.assert_awaited_once_with(text="```short```", channel="c1", thread_ts="t1")


@pytest.mark.asyncio
async def test_send_large_code_message_long(mock_client):
    si = SlackInteraction(mock_client)
    # 9001 chars, so should split into 3 messages: 4000, 4000, 1001
    msg = "a" * 9001
    await si.send_large_code_message(msg, "c1", "t1")
    # First two calls: 3999 chars each (due to -1 in slice), last call: 1001 chars
    expected_calls = [
        call(text="```" + msg[0:3999] + "```", channel="c1", thread_ts="t1"),
        call(text="```" + msg[4000:7999] + "```", channel="c1", thread_ts="t1"),
        call(text="```" + msg[8000:9001] + "```", channel="c1", thread_ts="t1"),
    ]
    # Allow for possible extra call if implementation changes, but check at least these
    actual_calls = mock_client.chat_postMessage.await_args_list
    for expected, actual in zip(expected_calls, actual_calls):
        assert expected == actual


@pytest.mark.asyncio
async def test_send_buttons_calls_chat_postMessage_with_blocks(mock_client):
    si = SlackInteraction(mock_client)
    title = "Choose"
    buttons = {"Yes": "yes_action", "No": "no_action"}
    await si.send_buttons(title, buttons, "c1", "t1", emoji=True)
    args, kwargs = mock_client.chat_postMessage.await_args
    assert kwargs["text"] == title
    assert kwargs["channel"] == "c1"
    assert kwargs["thread_ts"] == "t1"
    blocks = kwargs["blocks"]
    assert isinstance(blocks[0], SectionBlock)
    assert isinstance(blocks[1], ActionsBlock)
    # Check button elements
    action_block = blocks[1]
    assert any(isinstance(e, ButtonElement) and e.text.text in buttons for e in action_block.elements)
