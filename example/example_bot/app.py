import os
import asyncio
from dotenv import load_dotenv
import json
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from build_the_bot.interaction import SlackInteraction
from build_the_bot.nlp.chat_gpt import ChatGPT
from build_the_bot.state import AppState, Form, Context

FORMS = {"jira_support_ticket_form": Form(["title", "description"])}
INTENTS = {"fallback": "respond_other", "Hello": "respond_hello", "Jira Support Ticket": "respond_jira_support_ticket"}

CHATGPT_DEPLOYMENT_NAME = "YOUR CHATGPT DEPLOYMENT/MODEL NAME"
CHATGPT_API_VERSION = "YOUR CHATGPT API VERSION"
CHATGPT_ENDPOINT = "YOUR AZURE OPENAI ENDPOINT"
DATA_FOLDER_PATH = "data"

# load prompts and data
prompts_path = os.path.join(DATA_FOLDER_PATH, "prompts.json")
intent_data_path = os.path.join(DATA_FOLDER_PATH, "example_intent.json")
with open(prompts_path, "r", encoding="utf-8") as prompts:
    prompts = json.load(prompts)
with open(intent_data_path, "r", encoding="utf-8") as intent_data:
    intent_data = json.load(intent_data)
intent_prompt = prompts["intent"]

# Initializes your app with your bot token and signing secret
load_dotenv()
app = AsyncApp(
    token=os.environ.get("SLACK_BOT_TOKEN"),
)
slack_interaction = SlackInteraction(app.client)
state = AppState(FORMS, slack_interaction)


@app.event("message")
async def message(args):
    # only respond to DMs
    if args.event["channel_type"] != "im":
        return
    # ensure its a new message and not a retry due to Slack <3 sec response requirement
    message_id = args.body["event_id"]
    if not state.new_event(message_id):
        return
    await args.ack()

    user_message = args.event.get("text")
    user_id = args.event["user"]
    channel_id = args.event["channel"]
    context = Context(user_id=user_id, channel_id=channel_id, user_message=user_message)
    if state.new_user(context):
        state.add_user(context)
    elif state.new_user_context(context):
        state.add_new_user_context(context)
    user_intent = state.get_user_current_intent(context)
    if not user_intent:
        api_key = os.environ["CHATGPT_API_KEY"]
        gpt = ChatGPT(api_key, CHATGPT_DEPLOYMENT_NAME, CHATGPT_API_VERSION, CHATGPT_ENDPOINT)
        user_intent = gpt.run_recognition(user_message, intent_prompt, intent_data)
        state.set_user_intent(user_intent, context)

    await state.handle_intent(INTENTS, user_intent, context)


async def main():
    app_token = os.environ["APP_TOKEN"]
    handler = AsyncSocketModeHandler(app, app_token)
    await handler.start_async()


if __name__ == "__main__":
    asyncio.run(main())
