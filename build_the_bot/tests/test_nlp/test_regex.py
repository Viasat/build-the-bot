from build_the_bot.nlp.regex import entity_recognition
from build_the_bot.nlp.regex import find_after_term


class TestEntityRecognition:
    def test_term_present_case_insensitive(self):
        user_message = "Run on dev"
        possible_entity_values = ["dev", "staging"]
        assert entity_recognition(user_message, possible_entity_values) == "dev"

    def test_multiple_terms_first_match(self):
        user_message = "Run on staging and dev"
        possible_entity_values = ["dev", "staging"]
        # Should return "dev" because it's first in the list, even if "staging" appears first in the message
        assert entity_recognition(user_message, possible_entity_values) == "dev"

    def test_no_term_found(self):
        user_message = "run the script"
        possible_entity_values = ["dev", "staging"]
        assert entity_recognition(user_message, possible_entity_values) is None

    def test_term_with_regex_special_characters(self):
        user_message = "run on dev-1"
        possible_entity_values = ["dev-1", "staging"]
        assert entity_recognition(user_message, possible_entity_values) == "dev-1"

    def test_empty_possible_entity_values(self):
        user_message = "run the script on dev"
        possible_entity_values = []
        assert entity_recognition(user_message, possible_entity_values) is None

    def test_empty_user_message(self):
        user_message = ""
        possible_entity_values = ["dev", "staging"]
        assert entity_recognition(user_message, possible_entity_values) is None


class TestFindAfterTerm:
    def test_returns_substring_after_term(self):
        user_message = "test script1"
        term = "test"
        assert find_after_term(user_message, term) == "script1"

    def test_case_insensitive_match(self):
        user_message = "TEST script1"
        term = "test"
        assert find_after_term(user_message, term) == "script1"

    def test_term_at_end_returns_empty_string(self):
        user_message = "run a test"
        term = "test"
        assert find_after_term(user_message, term) == ""

    def test_term_not_present_returns_none(self):
        user_message = "hello"
        term = "test"
        assert find_after_term(user_message, term) is None

    def test_multiple_occurrences_returns_after_first(self):
        user_message = "test script1 and test script2"
        term = "test"
        assert find_after_term(user_message, term) == "script1 and test script2"

    def test_whitespace_after_term_is_stripped(self):
        user_message = "test            script1"
        term = "test"
        assert find_after_term(user_message, term) == "script1"

    def test_empty_user_message_returns_none(self):
        user_message = ""
        term = "test"
        assert find_after_term(user_message, term) is None

    def test_empty_term_returns_full_message(self):
        user_message = "test script1"
        term = ""
        assert find_after_term(user_message, term) == "test script1"
