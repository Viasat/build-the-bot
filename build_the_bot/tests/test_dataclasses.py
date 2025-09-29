from build_the_bot.state import Context, Form


class TestDataClasses:
    def test_context_init(self):
        ctx = Context(user_id="u1", channel_id="c1", thread_id="t1", user_message="hello", event="msg")
        assert ctx.user_id == "u1"
        assert ctx.channel_id == "c1"
        assert ctx.thread_id == "t1"
        assert ctx.user_message == "hello"
        assert ctx.event == "msg"

    def test_form_init(self):
        form = Form(inputs=["title", "description"])
        assert not form.filled
        assert form.inputs == {"title": None, "description": None}
        assert form.requested_input is None
