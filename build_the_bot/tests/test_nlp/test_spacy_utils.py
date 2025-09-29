import pytest
from unittest.mock import patch, MagicMock
from build_the_bot.nlp import spacy_utils


@pytest.mark.asyncio
class TestEntityRecognition:
    @patch("spacy.load")
    async def test_entity_recognition_returns_entities(self, mock_load):
        # Mock spaCy pipeline and doc
        mock_ent = MagicMock()
        mock_ent.label_ = "server"
        mock_ent.text = "dev"
        mock_doc = MagicMock()
        mock_doc.ents = [mock_ent]
        mock_nlp = MagicMock(return_value=mock_doc)
        mock_load.return_value = mock_nlp

        result = await spacy_utils.entity_recognition("run on dev", "dummy_path")
        assert result == {"server": "dev"}
        mock_load.assert_called_once_with("dummy_path")

    @patch("spacy.load")
    async def test_entity_recognition_no_entities(self, mock_load):
        mock_doc = MagicMock()
        mock_doc.ents = []
        mock_nlp = MagicMock(return_value=mock_doc)
        mock_load.return_value = mock_nlp

        result = await spacy_utils.entity_recognition("No entities here", "dummy_path")
        assert result == {}
