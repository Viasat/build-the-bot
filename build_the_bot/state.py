"""
Classes and utilities to maintain the bot's recognition of where it is in each conversation.
"""

import copy
import dataclasses
from typing import Dict
from build_the_bot.interaction import SlackInteraction


ask_for_input_map = {}
validate_input_map = {}


@dataclasses.dataclass
class Context:
    """
    Holds the who, what and where of who the bot is currently talking to.
    """

    def __init__(self, user_id, channel_id, thread_id=None, user_message: str = None, event=None):
        self.user_id = user_id
        self.channel_id = channel_id
        self.thread_id = thread_id
        self.user_message = user_message
        self.event = event


@dataclasses.dataclass
class Form:
    """
    Defines the inputs a user must provide, their values once the user has provided them,
    if they have provided them all and which one the bot has asked for.
    """

    def __init__(self, inputs):
        self.filled: bool = False
        self.inputs: Dict[str, str] = {input: None for input in inputs}
        self.requested_input: str = None


class UserState:
    """
    Defines and maintains the state of all the bot's supported forms for a user and the users current intent.
    """

    def __init__(self, forms: Dict[str, Form], channel_id, thread_id=None) -> None:
        self.app_forms = forms
        self.current_intents = {}
        self.forms: Dict[str, Dict[str, Dict[str, Form]]] = {}
        self.add_new_user_context(channel_id, thread_id)

    def new_user_context(self, channel_id, thread_id=None):
        if channel_id not in self.forms:
            return True
        elif thread_id and thread_id not in self.forms[channel_id]:
            return True
        return False

    def add_new_user_context(self, channel_id, thread_id=None):
        if thread_id:
            self.forms[channel_id] = {}
            self.forms[channel_id][thread_id] = copy.deepcopy(self.app_forms)
            self.current_intents[channel_id] = {}
            self.current_intents[channel_id][thread_id] = None
        else:
            self.forms[channel_id] = {}
            self.forms[channel_id]["dm"] = copy.deepcopy(self.app_forms)
            self.current_intents[channel_id] = {}
            self.current_intents[channel_id]["dm"] = None

    def set_intent(self, intent, channel_id, thread_id=None):
        if thread_id:
            self.current_intents[channel_id][thread_id] = intent
        else:
            self.current_intents[channel_id]["dm"] = intent

    def get_current_intent(self, channel_id, thread_id=None):
        if thread_id:
            return self.current_intents[channel_id][thread_id]
        else:
            return self.current_intents[channel_id]["dm"]

    def get_form(self, form_key, channel_id, thread_id=None):
        if thread_id:
            return self.forms[channel_id][thread_id][form_key]
        else:
            return self.forms[channel_id]["dm"][form_key]


class AppState:
    """
    A class to maintain the state of the App and its users
    """

    def __init__(self, forms: Dict[str, Form], interaction: SlackInteraction):
        """
        Initilize an AppState object
        :param {str: Form} forms: the forms the app will use
        :param  interaction: an instance of a class defined by the abstract Interaction class
        """
        self.messages = []
        self.users: Dict[str, UserState] = {}
        self.forms: Dict[str, Form] = forms
        self.interaction = interaction

    def add_user(self, context: Context):
        """
        Add a user to the users dictionary.
        :param Context context: Context object holding information about the current user interacting with the app
        """
        self.users[context.user_id] = UserState(self.forms, context.channel_id, context.thread_id)

    def new_user(self, context: Context):
        """
        Check if the user has been added to the AppState yet
        :param Context context: Context object holding information about the current user interacting with the app
        :return bool: True if the user is in the users dictionary, False otherwise.
        """
        if context.user_id in self.users:
            return False
        return True

    def new_user_context(self, context: Context):
        """
        Checks if the user has interacted in this channel and thread before
        :param Context context: Context object holding information about the current user interacting with the app
        :return bool: True if the user has interacted in this channel AND thread before, False otherwise.
        """
        if self.new_user(context):
            return True
        return self.users[context.user_id].new_user_context(context.channel_id, context.thread_id)

    def add_new_user_context(self, context: Context):
        """
        Adds the new user context to the users dictionary
        :param Context context: Context object holding information about the current user interacting with the app
        """
        self.users[context.user_id].add_new_user_context(context.channel_id, context.thread_id)

    def set_user_intent(self, intent, context: Context):
        """
        Sets a user's current intent for the given context
        :param str intent: The user's current intent to set
        :param Context context: Context object holding information about the current user interacting with the app
        """
        self.users[context.user_id].set_intent(intent, context.channel_id, context.thread_id)

    def get_user_current_intent(self, context: Context):
        """
        Retrieves the user's current intent for the given context
        :param Context context: Context object holding information about the current user interacting with the app
        return str: The user;s current intent for the given context
        """
        return self.users[context.user_id].get_current_intent(context.channel_id, context.thread_id)

    def new_event(self, message_id):
        """
        Check if the event is a new one because Slack resends them if the bot hasn't messaged in 3 seconds.
        :param str message_id: the uuid of the event/message
        """
        # don't let the list get too long
        if len(self.messages) > 100:
            self.messages.pop(0)
        if message_id in self.messages:
            return False
        else:
            self.messages.append(message_id)
            return True

    async def clear_state(self, context: Context):
        """
        Clear all forms and user state for the given context to allow for a new user intent.
        :param Context context: Context object holding information about the current user interacting with the app
        """
        if context.thread_id:
            forms_to_clear = self.users[context.user_id].forms[context.channel_id][context.thread_id]
            self.users[context.user_id].current_intents[context.channel_id][context.thread_id] = None
        else:
            forms_to_clear = self.users[context.user_id].forms[context.channel_id]["dm"]
            self.users[context.user_id].current_intents[context.channel_id]["dm"] = None
        for _, form in forms_to_clear.items():
            form.filled = False
            form.requested_input = None
            for input_name in form.inputs:
                form.inputs[input_name] = None

    async def handle_form(self, context: Context, form_key):
        """
        Save the user's message to the provided form and the requested input.
        Call validation if it exists and ask for the next input if the form is not filled.
        :param Context context: Context object holding information about the current user interacting with the app
        :param str form_key: the form to save the input to
        """
        form = self.users[context.user_id].get_form(form_key, context.channel_id, context.thread_id)
        if context.user_message == "q":
            await self.clear_state(context)
            await self.interaction.send_message(
                message="Quitting.", channel_id=context.channel_id, thread_id=context.thread_id
            )
            return
        if form.requested_input:
            requested_input = form.requested_input
            if validate_input_map.get(requested_input):
                if not await validate_input_map[requested_input](self, context, form_key, context.user_message):
                    return
            else:
                form.inputs[requested_input] = context.user_message
            form.requested_input = None
        for input_name in form.inputs.keys():
            if not form.inputs[input_name]:
                form.requested_input = input_name
                await ask_for_input_map[input_name](self, context)
                return
        form.filled = True

    async def handle_intent(self, intents: Dict[str, str], intent, context):
        """
        Trigger the business logic based on the user's intent
        Respond to the inventory status intent.
        :param dict[str, str] intents: a dictionary mapping the intent name to the function name to trigger in
            business.py
        :param str intent: the user's intent
        :param Context context: Context object holding information about the current user interacting with the app
        """
        import business

        response_func_name = intents.get(intent, None)
        if not response_func_name:
            response_func_name = intents["fallback"]
        response_func = getattr(business, response_func_name)
        await response_func(self, context)

    def set_input(self, context: Context, form_key, input_name, input_value):
        """
        Save the user's input.
        :param Context context: Context object holding information about the current user interacting with the app
        :param str form_key: the form to save the input to
        :param str input_name: name of the input to save to
        :param str input_value: the input value to save
        """
        self.users[context.user_id].get_form(form_key, context.channel_id, context.thread_id).inputs[
            input_name
        ] = input_value

    def get_input(self, context: Context, form_key, input_name):
        """
        Retrieves the user's input.
        :param Context context: Context object holding information about the current user interacting with the app
        :param str form_key: the form to retrieve the input from
        :param str input_name: name of the input to retrieve
        """
        return self.users[context.user_id].get_form(form_key, context.channel_id, context.thread_id).inputs[input_name]

    def get_form(self, context: Context, form_key):
        """
        Retrieves the form associated with the user context passed.
        :param Context context: Context object holding information about the current user interacting with the app
        :param str form_key: the form to retrieve
        """
        return self.users[context.user_id].get_form(form_key, context.channel_id, context.thread_id)


def ask_for_input(input_name):
    """
    defines ask_for_[input_name] decorator for handle_form
    """

    def input_map_decorator(func):
        ask_for_input_map[input_name] = func
        return func

    return input_map_decorator


def validate_input(input_name):
    """
    defines validate_[input_name] decorator for handle_form
    """

    def validate_slot_map_decorator(func):
        validate_input_map[input_name] = func
        return func

    return validate_slot_map_decorator
