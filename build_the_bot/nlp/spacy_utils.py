"""
A module that utilizes spaCy models.
"""

import spacy


async def entity_recognition(user_message, model_path):
    """ "
    Runs a spaCy model to detect entities in a user message
    :param str user_message: the user's message
    :param str model_path: path to the model

    """
    nlp_ner = spacy.load(model_path)
    doc = nlp_ner(user_message)
    ent_dict = {}
    for ent in doc.ents:
        ent_dict[ent.label_] = ent.text
    return ent_dict
