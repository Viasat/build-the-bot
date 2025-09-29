from build_the_bot.state import AppState, Context


async def create_jira_support_ticket(title, description, bot_state: AppState, context: Context):
    """
    Creates a Jira support ticket.
    :param str title: title/summary of the ticket
    :param str description: description of the ticket
    :param AppState bot_state: AppState object tracking the state of the app
    :param Context context: Context object holding information about the current user interacting with the app
    """
    await bot_state.interaction.send_message(
        message=f"<jira link with ticket created> \nTitle: {title} \nDescription: {description}",
        channel_id=context.channel_id,
    )
