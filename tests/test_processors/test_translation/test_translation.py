import pytest
import json

from my_flask_app.processors.translation.gemini_translator import GeminiTranslator


def test_gemini_translator_initialization(monkeypatch):
    """Ensure translator initializes without requiring a real API key."""
    monkeypatch.setattr(
        "google.generativeai.configure",
        lambda **kwargs: None
    )

    class DummyModel:
        def __init__(self, name):
            self.name = name

    monkeypatch.setattr(
        "google.generativeai.GenerativeModel",
        lambda model_name: DummyModel(model_name)
    )

    translator = GeminiTranslator()

    assert translator.models is not None
    assert "fast" in translator.models
    assert "quality" in translator.models
    assert translator.models["fast"].name == translator.models["fast"].name


def test_prompt_format_basic(monkeypatch):
    """Verify that prompt includes all important details."""
    monkeypatch.setattr("google.generativeai.configure", lambda **k: None)
    monkeypatch.setattr(
        "google.generativeai.GenerativeModel",
        lambda model_name: object()
    )

    translator = GeminiTranslator()

    texts = ["こんにちは"]

    prompt = translator._build_translation_prompt(
        texts,
        source_lang="ja",
        target_lang="en",
        context=None
    )

    assert "こんにちは" in prompt
    assert "from ja to en" in prompt
    assert "OUTPUT FORMAT" in prompt


def test_parse_translation_response(monkeypatch):
    """Ensure JSON responses are parsed correctly into a list of strings."""
    monkeypatch.setattr("google.generativeai.configure", lambda **k: None)
    monkeypatch.setattr(
        "google.generativeai.GenerativeModel",
        lambda model_name: object()
    )

    translator = GeminiTranslator()

    original = ["A", "B"]
    fake_json = json.dumps(["X", "Y"])

    result = translator._parse_translation_response(fake_json, original)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0] == "X"
    assert result[1] == "Y"


def test_translate_with_mocked_api(monkeypatch):
    """Mock entire translation flow to ensure correct mapping."""
    monkeypatch.setattr("google.generativeai.configure", lambda **k: None)
    monkeypatch.setattr(
        "google.generativeai.GenerativeModel",
        lambda model_name: object()
    )

    translator = GeminiTranslator()

    fake_response = json.dumps(["Hello world"])

    monkeypatch.setattr(
        translator,
        "_translate_with_retry",
        lambda model, prompt: fake_response
    )

    text_data = [
        {
            "bubble": {"x": 0, "y": 0, "width": 100, "height": 50},
            "text": "こんにちは",
        }
    ]

    result = translator.translate(
        text_data,
        source_lang="ja",
        target_lang="en",
        model_type="fast",
        context=None,
    )

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["text"] == "Hello world"
    assert "translation_confidence" in result[0]
    assert "bubble" in result[0]


def test_retry_logic(monkeypatch):
    """Simulate failures until final retry and ensure it raises."""
    class FailingModel:
        def generate_content(self, *args, **kwargs):
            raise RuntimeError("FAIL HARD")

    monkeypatch.setattr("google.generativeai.configure", lambda **k: None)
    monkeypatch.setattr(
        "google.generativeai.GenerativeModel",
        lambda model_name: FailingModel()
    )

    translator = GeminiTranslator()
    translator.max_retries = 3
    translator.retry_delay = 0

    with pytest.raises(RuntimeError):
        translator._translate_with_retry(FailingModel(), "prompt")
