"""
A module to process natural language utilizing regex
"""

import re


def entity_recognition(user_message, possible_entity_values):
    """
    Search for terms in a user message
    :param str user_message: the user's message
    :param [str] possible_entity_values: values to search for in the user message
    :return str: Return the first possible term found, None if no terms found.
    """
    for term in possible_entity_values:
        if re.search(term, user_message, re.IGNORECASE):
            return term
    return None


def find_after_term(user_message, term):
    """
    Grab everything after a specified term in a user message
    :param str user_message: the user's message
    :param str term: the string to search for and grab everything after
    :return str: Return the substring after the term
    """
    pattern = rf".*?{term}(.*)"
    result = re.search(pattern, user_message, re.IGNORECASE)
    if result:
        content_after_term = result.group(1).lstrip()  # Remove whitespace at the start
        return content_after_term
