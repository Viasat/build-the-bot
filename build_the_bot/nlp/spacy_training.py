"""
Module to create spacy models.
"""

import json
import random

import spacy
from spacy.tokens import DocBin
from spacy.util import filter_spans


def load_examples_from_json_file(json_file_path):  # pragma: no cover
    """
    Opens and loads the training data to a python object
    :param str json_file_path: file path to the data json file
    :return: a Python list or dict depending on the passed json
    """
    with open(json_file_path, "r", encoding="utf-8") as json_file:
        examples = json.load(json_file)
    return examples


def convert_user_assistant_examples_to_docs(nlp, examples, entity_names):
    """
    Converts the training data to spaCy docs
    :param spacy.Language nlp: spaCy Language obeject
    :param dict examples: data to train the model on in the following format:
        [{"role":"user", "content": "user message with entities"},
        {"role":"assistant":"{"entity_1": "entity_1_value", "entity_2": "entity_2_value"}"]
    :param [str] entity_names: list of entity names for the model to recognize.
        Names must match the entities defined in the json provided.
    :return [spacy.Doc]: A list of spaCy Document objects with annotated entities.
    """
    docs = []
    for i in range(0, len(examples) - 1, 2):
        user_message = examples[i]["content"]
        entity_dict = json.loads(examples[i + 1]["content"])

        ents = []
        doc = nlp.make_doc(user_message)

        for entity_name in entity_names:
            if entity_name in entity_dict:
                start_index = user_message.index(entity_dict[entity_name])
                end_index = start_index + len(entity_dict[entity_name])
                entity_span = doc.char_span(start_index, end_index, label=entity_name, alignment_mode="contract")
                if entity_span is None:
                    print(f"Skipping {entity_name} span: {user_message}")  # pragma: no cover
                else:
                    ents.append(entity_span)

        filtered_ents = filter_spans(ents)
        doc.ents = filtered_ents
        docs.append(doc)
    return docs


def create_spacy_files_from_user_assistant_data(
    json_file_path, entity_names, training_size, test_size, training_output_path, test_output_path
):
    """
    Creates a spaCy training file for an entity recongition model.
    :param str json_file_path: file path to a json file with the following format:
        [{"role":"user", "content": "user message with entities"},
        {"role":"assistant":"{"entity_1": "entity_1_value", "entity_2": "entity_2_value"}"]
    :param [str] entity_names: list of entity names for the model to recognize.
        Names must match the entities defined in the json provided.
    :param float training_size: percentage of the data to use for training
    :param float test_size: percentage of the data to use for test validation. Should equal 1-training_size.
    :param str training_output_path: path to save the spaCy training file
    :param str test_output_path: path to save the spaCy test file
    """
    examples = load_examples_from_json_file(json_file_path)
    nlp = spacy.blank("en")

    docs = convert_user_assistant_examples_to_docs(nlp, examples, entity_names)

    random.seed(0)
    random.shuffle(docs)

    train_size = int(len(docs) * training_size)
    train_docs = docs[:train_size]
    test_docs = docs[train_size : train_size + int(len(docs) * test_size)]

    train_bin = DocBin(docs=train_docs)
    train_bin.to_disk(training_output_path)

    test_bin = DocBin(docs=test_docs)
    test_bin.to_disk(test_output_path)
