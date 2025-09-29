from build_the_bot.state import Form, UserState


class TestInit:
    def test_userstate_init_dm(self):
        forms = {"jira_ticket": Form(["title", "description"])}
        user_state = UserState(forms, channel_id="c1")
        assert "c1" in user_state.forms
        assert "dm" in user_state.forms["c1"]
        assert user_state.get_form("jira_ticket", "c1", "dm") is not forms["jira_ticket"]
        assert user_state.current_intents["c1"]["dm"] is None

    def test_userstate_init_thread(self):
        forms = {"jira_ticket": Form(["title", "description"])}
        user_state = UserState(forms, channel_id="c1", thread_id="t1")
        assert "c1" in user_state.forms
        assert "t1" in user_state.forms["c1"]
        assert isinstance(user_state.get_form("jira_ticket", "c1", "t1"), Form)
        assert user_state.get_form("jira_ticket", "c1", "t1") is not forms["jira_ticket"]
        assert user_state.current_intents["c1"]["t1"] is None


class TestGetForm:
    def test_get_form_dm(self):
        forms = {"jira_ticket": Form(["title", "description"])}
        user_state = UserState(forms, channel_id="c1")
        form = user_state.get_form("jira_ticket", "c1")
        assert isinstance(form, Form)
        assert form.inputs == {"title": None, "description": None}
        assert form is not forms["jira_ticket"]

    def test_get_form_thread(self):
        forms = {"jira_ticket": Form(["title", "description"])}
        user_state = UserState(forms, channel_id="c1", thread_id="t1")
        form = user_state.get_form("jira_ticket", "c1", "t1")
        assert isinstance(form, Form)
        assert form.inputs == {"title": None, "description": None}
        assert form is not forms["jira_ticket"]


class TestIntent:
    def test_get_set_intent_dm(self):
        no_forms = {}
        user_state = UserState(no_forms, channel_id="c1")
        user_state.set_intent("greet", "c1")
        assert user_state.get_current_intent("c1") == "greet"

    def test_get_set_intent_thread(self):
        no_forms = {}
        user_state = UserState(no_forms, channel_id="c1")
        user_state.set_intent("greet", "c1", "t1")
        assert user_state.get_current_intent("c1", "t1") == "greet"
