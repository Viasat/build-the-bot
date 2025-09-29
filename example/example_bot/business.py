from build_the_bot.state import ask_for_input, AppState, Context
import action


async def respond_hello(bot_state: AppState, context: Context):
    """
    Respond to the hello intent.
    :param AppState bot_state: AppState object tracking the state of the app
    :param Context context: Context object holding information about the current user interacting with the app
    """
    await bot_state.interaction.send_message(message="Hello", channel_id=context.channel_id)
    await bot_state.clear_state(context)


async def respond_other(bot_state, context: Context):
    """
    Respond to an unrecognized intent and report what the bot can do.
    :param AppState bot_state: AppState object tracking the state of the app
    :param Context context: Context object holding information about the current user interacting with the app
    """
    await bot_state.interaction.send_message(
        message="Could not determine your request. I am currently able to assist you with:\n"
        "• submitting a support request jira ticket \n",
        channel_id=context.channel_id,
    )
    await bot_state.clear_state(context)


@ask_for_input("title")
async def ask_for_title(bot_state: AppState, context: Context):
    """
    Ask the user to provide the title input.
    :param AppState bot_state: AppState object tracking the state of the app
    :param Context context: Context object holding information about the current user interacting with the app
    """
    await bot_state.interaction.send_message(
        message="What would you like the title to be? [type 'q' to quit]", channel_id=context.channel_id
    )


@ask_for_input("description")
async def ask_for_description(bot_state: AppState, context: Context):
    """
    Ask the user to provide the blueprint name input.
    :param AppState bot_state: AppState object tracking the state of the app
    :param Context context: Context object holding information about the current user interacting with the app
    """
    await bot_state.interaction.send_message(
        message="What would you like the description to be? [type 'q' to quit]", channel_id=context.channel_id
    )


async def respond_jira_support_ticket(bot_state: AppState, context: Context):
    """
    Respond to the jira support ticket user intent.
    :param AppState bot_state: AppState object tracking the state of the app
    :param Context context: Context object holding information about the current user interacting with the app
    """

    form = bot_state.get_form(context, "jira_support_ticket_form")
    if not form.requested_input:
        await bot_state.interaction.send_message(
            message="I can create a Jira ticket for you!", channel_id=context.channel_id
        )
    await bot_state.handle_form(context, "jira_support_ticket_form")
    if form.filled:
        await bot_state.interaction.send_message(message="Adding users...", channel_id=context.channel_id)
        await action.create_jira_support_ticket(
            form.inputs["title"],
            form.inputs["description"],
            bot_state,
            context,
        )
        await bot_state.clear_state(context)
