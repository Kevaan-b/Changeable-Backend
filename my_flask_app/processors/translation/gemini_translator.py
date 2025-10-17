"""
Gemini-based translation implementation.
"""
import google.generativeai as genai
import json
import time
from processors.translation.base_translator import BaseTranslator
from config.settings import Config


class GeminiTranslator(BaseTranslator):
    """Translation processor using Google Gemini models."""

    def __init__(self):
        """Initialize Gemini translator."""
        try:
            genai.configure(api_key=Config.GEMINI_API_KEY)

            # Initialize different models for different use cases
            self.models = {
                "fast": genai.GenerativeModel(Config.GEMINI_FLASH_MODEL),
                "quality": genai.GenerativeModel(Config.GEMINI_PRO_MODEL),
            }

            self.max_retries = Config.TRANSLATION_MAX_RETRIES
            self.retry_delay = Config.TRANSLATION_RETRY_DELAY

        except Exception as e:
            raise e

    def translate(self,
        text_data: list[dict],
        source_lang: str,
        target_lang: str,
        model_type: str = "fast",
    ) -> list[dict]:
        """
        Translate extracted text data using Gemini.
        """
        if not text_data:
            return []

        try:
            prompt = self._build_translation_prompt(
                text_data, source_lang, target_lang
            )

            model = self.models.get(model_type, self.models["fast"])

            response = self._translate_with_retry(model, prompt)

            translated_data = self._parse_translation_response(response, text_data)

            return translated_data

        except Exception as e:
            return text_data

    def _build_translation_prompt(
        self, text_data: list[dict], source_lang: str, target_lang: str
    ) -> str:
        """Build comprehensive translation prompt for Gemini."""

        texts = [item["text"] for item in text_data]

        prompt = f"""
                    You are a professional translator specializing in visual media (comics, manga, graphic novels).

                    Task: Translate the following text elements from {source_lang} to {target_lang}.

                    IMPORTANT REQUIREMENTS:
                    1. Maintain the original meaning and tone.
                    2. Consider the context of visual media (speech bubbles, sound effects, etc.).
                    3. Keep translations concise to fit in speech bubbles.
                    4. Preserve emotions and character voice.
                    5. Handle sound effects appropriately.
                    6. Return translations in the same order as input.

                    INPUT TEXTS:
                    {json.dumps(texts, ensure_ascii=False, indent=2)}

                    OUTPUT FORMAT:
                    Return a JSON array of translated strings in the exact same order as input.
                    Example: ["translated text 1", "translated text 2", ...]

                    TRANSLATION:
                    """
        return prompt

    def _translate_with_retry(self, model, prompt: str) -> str:
        """Perform translation with retry logic."""
        last_error = None

        for attempt in range(self.max_retries):
            try:
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                        max_output_tokens=4000,
                    ),
                )

                if hasattr(response, "text") and response.text:
                    return response.text
                else:
                    raise ValueError("Empty or invalid response from Gemini")

            except Exception as e:
                last_error = e

                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2**attempt))  # Exponential backoff

        raise last_error

    def _parse_translation_response(
        self, response: str, original_data: list[dict]
    ) -> list[dict]:
        """Parse Gemini response and merge with original data."""
        try:
            response_clean = response.strip()

            if response_clean.startswith("```json"):
                response_clean = response_clean.strip("`")
                response_clean = response_clean.replace("json", "", 1).strip()
            elif response_clean.startswith("```"):
                response_clean = response_clean.strip("`").strip()

            translations = json.loads(response_clean)

            if not isinstance(translations, list):
                raise ValueError("Response is not a list")

            result = []
            for i, original in enumerate(original_data):
                if i < len(translations):
                    result.append(
                        {
                            **original,
                            "translated_text": translations[i],
                            "translation_confidence": 0.9,
                        }
                    )
                else:
                    result.append(
                        {
                            **original,
                            "translated_text": original["text"],
                            "translation_confidence": 0.0,
                        }
                    )

            return result

        except Exception as e:
            return [
                {
                    **item,
                    "translated_text": item["text"],
                    "translation_confidence": 0.0,
                }
                for item in original_data
            ]
