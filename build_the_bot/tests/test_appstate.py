import pytest
import types
from build_the_bot.state import (
    Context,
    Form,
    AppState,
    ask_for_input,
    validate_input,
    ask_for_input_map,
    validate_input_map,
)


# Patch Interaction everywhere in state.py to a dummy class
class DummyInteraction:
    async def send_message(self, message, channel_id, thread_id=None):
        pass


@pytest.fixture()
def app():
    forms = {"jira_ticket": Form(["title", "description"])}
    return AppState(forms, DummyInteraction())


@pytest.fixture()
def context_dm():
    return Context(user_id="u1", channel_id="c1")


def make_context(user_id, channel_id, thread_id=None, user_message=None):
    return Context(user_id=user_id, channel_id=channel_id, thread_id=thread_id, user_message=user_message)


class TestNewUser:
    def test_new_user(self, app, context_dm):
        assert app.new_user(context_dm) is True
        app.add_user(context_dm)
        assert app.new_user(context_dm) is False

    def test_new_user_context(self, app):
        ctx = make_context(user_id="u1", channel_id="c1")
        # new user
        assert app.new_user_context(ctx) is True
        app.add_user(ctx)
        assert app.new_user_context(ctx) is False
        # same user, new channel
        ctx2 = make_context(user_id="u1", channel_id="c2", thread_id="t1")
        assert app.new_user_context(ctx2) is True
        app.add_user(ctx2)
        # same user, same channel, new thread
        ctx3 = make_context(user_id="u1", channel_id="c2", thread_id="t2")
        assert app.new_user_context(ctx3) is True

    def test_add_new_user_context(self, app):
        ctx = make_context(user_id="u1", channel_id="c1")
        app.add_user(ctx)
        ctx2 = make_context(user_id="u1", channel_id="c1", thread_id="t2")
        app.add_new_user_context(ctx2)
        assert app.new_user_context(ctx2) is False


class TestUserIntent:
    def test_get_set_user_intent(self, app, context_dm):
        app.add_user(context_dm)
        app.set_user_intent("greet", context_dm)
        assert app.get_user_current_intent(context_dm) == "greet"


class TestNewEvent:
    def test_new_event(self, app):
        assert app.new_event("msg1")
        assert not app.new_event("msg1")

    def test_new_event_filled(self, app):
        assert app.new_event("msg1")
        app.messages = [f"msg{i}" for i in range(101)]
        assert not app.new_event("msg1")


class TestClearState:
    @pytest.mark.asyncio
    async def test_clear_state(self, app, context_dm):
        app.add_user(context_dm)
        app.set_input(context_dm, "jira_ticket", "title", "create bot")
        app.set_input(context_dm, "jira_ticket", "description", "a bot to create tickets")
        await app.clear_state(context_dm)
        form = app.get_form(context_dm, "jira_ticket")
        assert form.inputs["title"] is None
        assert form.inputs["description"] is None
        assert not form.filled

    @pytest.mark.asyncio
    async def test_clear_state_thread(self, app):
        ctx = make_context(user_id="u1", channel_id="c1", thread_id="t1")
        app.add_user(ctx)
        app.set_input(ctx, "jira_ticket", "title", "create bot")
        app.set_input(ctx, "jira_ticket", "description", "a bot to create tickets")
        await app.clear_state(ctx)
        form = app.get_form(ctx, "jira_ticket")
        assert form.inputs["title"] is None
        assert form.inputs["description"] is None
        assert not form.filled


class TestHandleForm:
    @pytest.mark.asyncio
    async def test_handle_form_inital(self, app):
        ctx = make_context(user_id="u1", channel_id="c1", user_message="jira ticket")
        app.add_user(ctx)
        form = app.get_form(ctx, "jira_ticket")
        called = {"asked": False}

        async def fake_ask(self, context):
            called["asked"] = True

        ask_for_input_map["title"] = fake_ask
        await app.handle_form(ctx, "jira_ticket")
        assert called["asked"]
        assert form.requested_input == "title"
        assert not form.filled

    @pytest.mark.asyncio
    async def test_handle_form_filled(self, app):
        ctx = make_context(user_id="u1", channel_id="c1", user_message="a bot to create tickets")
        app.add_user(ctx)
        form = app.get_form(ctx, "jira_ticket")
        form.inputs["title"] = "build a bot"
        form.requested_input = "description"
        called = {"asked": False}

        async def fake_ask(self, context):
            called["asked"] = True

        ask_for_input_map["description"] = fake_ask
        await app.handle_form(ctx, "jira_ticket")
        assert not called["asked"]
        assert app.get_input(ctx, "jira_ticket", "description") == "a bot to create tickets"
        assert form.requested_input is None
        assert form.filled

    @pytest.mark.asyncio
    async def test_handle_form_quit(self, app):
        ctx = make_context(user_id="u1", channel_id="c1", user_message="q")
        app.add_user(ctx)
        form = app.get_form(ctx, "jira_ticket")
        called = {"asked": False}

        async def fake_ask(self, context):
            called["asked"] = True

        ask_for_input_map["title"] = fake_ask
        await app.handle_form(ctx, "jira_ticket")
        assert not called["asked"]
        # assert state was cleared
        assert form.requested_input is None
        assert not form.filled
        assert app.get_user_current_intent(ctx) is None
        assert app.get_form(ctx, "jira_ticket").inputs == {"title": None, "description": None}

    @pytest.mark.asyncio
    async def test_handle_form_invalid(self, app):
        ctx = make_context(user_id="u1", channel_id="c1", user_message="build a bot")
        app.add_user(ctx)
        form = app.get_form(ctx, "jira_ticket")
        form.requested_input = "title"
        called = {"validated": False}

        async def fake_validator(self, context, form_key, user_message):
            called["validated"] = True
            return False

        validate_input_map["title"] = fake_validator
        await app.handle_form(ctx, "jira_ticket")
        assert called["validated"]
        assert form.inputs["title"] is None
        assert form.requested_input == "title"


class TestHandleIntent:
    @pytest.mark.asyncio
    async def test_handle_intent(self, app, context_dm):
        called = {"ran": False}

        async def fake_func(self, context):
            called["ran"] = True

        intents = {"greet": "fake_func", "fallback": "fake_other_func"}
        import sys

        sys.modules["business"] = types.SimpleNamespace(fake_func=fake_func)
        await app.handle_intent(intents, "greet", context_dm)
        assert called["ran"]

    @pytest.mark.asyncio
    async def test_handle_intent_fallback(self, app):
        ctx = make_context(user_id="u1", channel_id="c1", user_message="meh")
        called = {"ran": False}

        async def fake_other_func(self, context):
            called["ran"] = True

        intents = {"greet": "fake_func", "fallback": "fake_other_func"}
        import sys

        sys.modules["business"] = types.SimpleNamespace(fake_other_func=fake_other_func)
        await app.handle_intent(intents, "other", ctx)
        assert called["ran"]


class TestInput:
    def test_set_and_get_input(self, app, context_dm):
        app.add_user(context_dm)
        app.set_input(context_dm, "jira_ticket", "title", "build a bot")
        assert app.get_input(context_dm, "jira_ticket", "title") == "build a bot"

    def test_get_form(self, app, context_dm):
        app.add_user(context_dm)
        form = app.get_form(context_dm, "jira_ticket")
        assert isinstance(form, Form)
        assert form.inputs == {"title": None, "description": None}

    def test_ask_for_input_and_validate_input(self):
        called = {}

        @ask_for_input("test")
        def ask_fn(self, context):
            called["ask"] = True

        @validate_input("test")
        def validate_fn(self, context, form_key, user_message):
            called["validate"] = True

        assert ask_for_input_map["test"] is ask_fn
        assert validate_input_map["test"] is validate_fn
        ask_fn(None, None)
        validate_fn(None, None, None, None)
        assert called["ask"]
        assert called["validate"]
