# tests/test_config/test_settings.py

import importlib

import pytest
import google.oauth2.service_account as sa

import my_flask_app.config.settings as settings


ENV_KEYS = [
    "USE_GPU_OCR",
    "OCR_CONFIDENCE_THRESHOLD",
    "OCR_ENHANCE_IMAGE",
    "GEMINI_API_KEY",
    "GEMINI_FLASH_MODEL",
    "GEMINI_PRO_MODEL",
    "TRANSLATION_MAX_RETRIES",
    "TRANSLATION_RETRY_DELAY",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "TYPESETTER_ENGINE",
]


def clear_relevant_env(monkeypatch):
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def test_config_defaults(monkeypatch):
    """
    When no relevant environment variables are set,
    Config should use its default values and not create credentials.
    """
    clear_relevant_env(monkeypatch)

    # Reload the settings module so class-level attributes are re-evaluated
    settings_reloaded = importlib.reload(settings)
    Config = settings_reloaded.Config

    # EasyOCR defaults
    assert Config.EASYOCR_LANGUAGES == ["en", "ko"]
    assert Config.USE_GPU_OCR is False
    assert Config.OCR_CONFIDENCE_THRESHOLD == 0.6
    assert Config.OCR_ENHANCE_IMAGE is True

    # Gemini defaults
    assert Config.GEMINI_API_KEY is None
    assert Config.GEMINI_FLASH_MODEL == "gemini-2.5-flash"
    assert Config.GEMINI_PRO_MODEL == "gemini-2.5-pro"

    # Translation defaults
    assert Config.TRANSLATION_MAX_RETRIES == 3
    assert Config.TRANSLATION_RETRY_DELAY == 2

    # Google Translate credentials should not be created without env var
    assert Config.GOOGLE_TRANSLATE_CREDENTIALS is None

    # File upload configuration
    assert Config.MAX_CONTENT_LENGTH == 16 * 1024 * 1024
    assert Config.ALLOWED_EXTENSIONS == {"png", "jpg", "jpeg", "gif", "zip"}

    # Typesetting defaults
    assert Config.TYPESETTER_ENGINE == "opencv"


def test_config_env_overrides(monkeypatch):
    """
    Environment variables should override defaults.
    We don't touch real Google credentials here.
    """
    clear_relevant_env(monkeypatch)

    # Set env vars to override defaults
    monkeypatch.setenv("USE_GPU_OCR", "TrUe")
    monkeypatch.setenv("OCR_CONFIDENCE_THRESHOLD", "0.85")
    monkeypatch.setenv("OCR_ENHANCE_IMAGE", "false")

    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")
    monkeypatch.setenv("GEMINI_FLASH_MODEL", "custom-flash")
    monkeypatch.setenv("GEMINI_PRO_MODEL", "custom-pro")

    monkeypatch.setenv("TRANSLATION_MAX_RETRIES", "5")
    monkeypatch.setenv("TRANSLATION_RETRY_DELAY", "10")

    monkeypatch.setenv("TYPESETTER_ENGINE", "pango")

    # Reload settings so that Config is re-evaluated with our env
    settings_reloaded = importlib.reload(settings)
    Config = settings_reloaded.Config

    # EasyOCR overrides
    assert Config.USE_GPU_OCR is True
    assert Config.OCR_CONFIDENCE_THRESHOLD == 0.85
    assert Config.OCR_ENHANCE_IMAGE is False

    # Gemini overrides
    assert Config.GEMINI_API_KEY == "test-api-key"
    assert Config.GEMINI_FLASH_MODEL == "custom-flash"
    assert Config.GEMINI_PRO_MODEL == "custom-pro"

    # Translation overrides
    assert Config.TRANSLATION_MAX_RETRIES == 5
    assert Config.TRANSLATION_RETRY_DELAY == 10

    # Typesetter override
    assert Config.TYPESETTER_ENGINE == "pango"

