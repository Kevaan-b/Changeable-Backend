"""
Gemini-based translation implementation.
"""
import google.generativeai as genai
from typing import List, Dict
import json
import logging
import time
from processors.translation.base_translator import BaseTranslator
from config.settings import Config

logger = logging.getLogger(__name__)


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

            logger.info("Gemini translator initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Gemini translator: {e}")
            raise

    def translate(
        self,
        text_data: List[Dict],
        source_lang: str,
        target_lang: str,
        model_type: str = "fast",
    ) -> List[Dict]:
        """
        Translate extracted text data using Gemini.
        """
        if not text_data:
            return []

        try:
            # Prepare translation prompt
            prompt = self._build_translation_prompt(
                text_data, source_lang, target_lang
            )

            # Get appropriate model
            model = self.models.get(model_type, self.models["fast"])

            # Perform translation with retry logic
            response = self._translate_with_retry(model, prompt)

            # Parse and validate response
            translated_data = self._parse_translation_response(response, text_data)

            logger.info(
                f"Successfully translated {len(translated_data)} text elements"
            )
            return translated_data

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            # Return original data as fallback
            return text_data

    def _build_translation_prompt(
        self, text_data: List[Dict], source_lang: str, target_lang: str
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
4. Preserve emotional nuance and character voice.
5. Handle onomatopoeia (sound effects) appropriately.
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
                logger.warning(f"Translation attempt {attempt + 1} failed: {e}")

                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2**attempt))  # Exponential backoff

        raise last_error

    def _parse_translation_response(
        self, response: str, original_data: List[Dict]
    ) -> List[Dict]:
        """Parse Gemini response and merge with original data."""
        try:
            response_clean = response.strip()

            # Handle cases where response might be wrapped in code fences
            if response_clean.startswith("```json"):
                response_clean = response_clean.strip("`")
                response_clean = response_clean.replace("json", "", 1).strip()
            elif response_clean.startswith("```"):
                response_clean = response_clean.strip("`").strip()

            # Parse JSON safely
            translations = json.loads(response_clean)

            if not isinstance(translations, list):
                raise ValueError("Response is not a list")

            if len(translations) != len(original_data):
                logger.warning(
                    f"Translation count mismatch: {len(translations)} vs {len(original_data)}"
                )

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
            logger.error(f"Failed to parse translation response: {e}")
            logger.debug(f"Response content: {response}")
            return [
                {
                    **item,
                    "translated_text": item["text"],
                    "translation_confidence": 0.0,
                }
                for item in original_data
            ]
