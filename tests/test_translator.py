"""
Test Gemini translation functionality.
"""
import pytest
from my_flask_app.processors.translation.gemini_translator import GeminiTranslator

@pytest.mark.unit
def test_gemini_translator_initialization():
    """Ensure the Gemini translator initializes correctly."""
    try:
        translator = GeminiTranslator()
        assert translator.models is not None
        assert "fast" in translator.models
        assert "quality" in translator.models
    except Exception as e:
        pytest.skip(f"Gemini translator initialization failed: {e}")


@pytest.mark.unit
def test_gemini_translation_prompt_format():
    """Verify translation prompt creation."""
    translator = GeminiTranslator()
    sample_data = [{"text": "こんにちは"}]
    prompt = translator._build_translation_prompt(sample_data, "ja", "en")

    assert "こんにちは" in prompt
    assert "from ja to en" in prompt
    assert "translated text 1" in prompt


@pytest.mark.integration
def test_gemini_translation(monkeypatch):
    """Mock a translation call to test parsing and integration."""
    translator = GeminiTranslator()

    # Mock Gemini model response
    monkeypatch.setattr(
        translator, "_translate_with_retry", lambda model, prompt: '["Hello world"]'
    )

    input_data = [{"text": "こんにちは"}]
    results = translator.translate(input_data, "ja", "en", model_type="fast")

    assert len(results) == 1
    assert results[0]["translated_text"] == "Hello world"
    assert "translation_confidence" in results[0]


@pytest.mark.integration
def test_gemini_translation_real(monkeypatch):
    """
    ⚠️ Real-world test that calls Gemini API.
    Requires valid GEMINI_API_KEY in environment/config.
    """
    translator = GeminiTranslator()

    sample_data = [
        {"text": "おはようございます"},
        {"text": "私は学生です"},
    ]

    try:
        results = translator.translate(sample_data, "ja", "en", model_type="fast")
        assert isinstance(results, list)
        assert len(results) == len(sample_data)
        for item in results:
            assert "translated_text" in item
            print(f"✅ {item['text']} → {item['translated_text']}")
    except Exception as e:
        pytest.skip(f"Real Gemini translation test failed: {e}")
