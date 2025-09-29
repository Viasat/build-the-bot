from build_the_bot.nlp import spacy_training
from unittest.mock import patch, MagicMock


class TestSpacyTraining:

    def test_convert_user_assistant_examples_to_docs(self):
        examples = [{"role": "user", "content": "run on dev"}, {"role": "assistant", "content": '{"server": "dev"}'}]
        nlp = MagicMock()
        doc = MagicMock()
        nlp.make_doc.return_value = doc
        entity = MagicMock()
        entity.label_ = "server"
        entity.text = "dev"
        # char_span returns the entity
        doc.char_span.return_value = entity
        # ents is set by the function
        doc.ents = []

        docs = spacy_training.convert_user_assistant_examples_to_docs(nlp, examples, ["server"])

        assert len(docs) == 1
        doc = docs[0]
        ents = list(doc.ents)
        assert len(ents) == 1
        assert ents[0].label_ == "server"
        assert ents[0].text == "dev"
        assert doc is nlp.make_doc.return_value

    def test_create_spacy_files_from_user_assistant_data(self, tmp_path):
        fake_examples = [
            {"role": "user", "content": "run on dev"},
            {"role": "assistant", "content": '{"server": "dev"}'},
        ]
        fake_docs = [MagicMock(), MagicMock(), MagicMock()]
        train_path = tmp_path / "train.spacy"
        test_path = tmp_path / "test.spacy"
        training_size = 0.67
        test_size = 0.33

        with (
            patch(
                "build_the_bot.nlp.spacy_training.load_examples_from_json_file", return_value=fake_examples
            ) as mock_load,
            patch("build_the_bot.nlp.spacy_training.convert_user_assistant_examples_to_docs", return_value=fake_docs),
            patch("build_the_bot.nlp.spacy_training.DocBin") as mock_docbin,
        ):
            mock_train_bin = MagicMock()
            mock_test_bin = MagicMock()
            # DocBin() should return different mocks for train and test
            mock_docbin.side_effect = [mock_train_bin, mock_test_bin]

            spacy_training.create_spacy_files_from_user_assistant_data(
                "fake.json", ["server"], training_size, test_size, str(train_path), str(test_path)
            )

            mock_load.assert_called_once_with("fake.json")
            mock_train_bin.to_disk.assert_called_once_with(str(train_path))
            mock_test_bin.to_disk.assert_called_once_with(str(test_path))

            # Assert correct doc split for training and test sizes
            train_docs_arg = mock_docbin.call_args_list[0][1]["docs"]
            test_docs_arg = mock_docbin.call_args_list[1][1]["docs"]
            expected_train_size = int(len(fake_docs) * training_size)
            expected_test_size = int(len(fake_docs) * test_size)
            assert len(train_docs_arg) == expected_train_size
            assert len(test_docs_arg) == expected_test_size
