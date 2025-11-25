import google.generativeai as genai
import json
from my_flask_app.processors.translation.base_translator import BaseTranslator
from my_flask_app.processors.translation.context_store import ContextStore
from my_flask_app.config.settings import Config
from my_flask_app.models.context import Context
import time


class GeminiTranslator(BaseTranslator):
    """Translation processor using Google Gemini models."""

    def __init__(self):
        """Initialize Gemini translator."""
        try:
            genai.configure(api_key=Config.GEMINI_API_KEY)

            self.models = {
                "fast": genai.GenerativeModel(Config.GEMINI_FLASH_MODEL),
                "quality": genai.GenerativeModel(Config.GEMINI_PRO_MODEL),
            }

            self.max_retries = Config.TRANSLATION_MAX_RETRIES
            self.retry_delay = Config.TRANSLATION_RETRY_DELAY

            self.context_store = ContextStore(Config.TRANSLATION_CONTEXT_PATH)

        except Exception as e:
            raise e

    def translate(
        self,
        text_data: list[dict],
        target_lang: str,
        model_type: str = "fast",
        context: Context = None
        ) -> list[dict]:
        """
        Translate extracted text data using Gemini.

        text_data is expected to be the OCR output:
        [
        {
            "bubble": {...},
            "text": "concatenated bubble text"
        },
        ...
        ]
        """
        if not text_data:
            return []

        try:
            flat_texts: list[str] = []
            for group in text_data:
                raw = group.get("text", "") or ""
                cleaned = raw.strip()
                if cleaned:
                    flat_texts.append(cleaned)

            if not flat_texts:
                return text_data

            print(flat_texts)
            prompt = self._build_translation_prompt(flat_texts, target_lang, context)

            model = self.models.get(model_type, self.models["fast"])

            response = self._translate_with_retry(model, prompt)
            print(response)

            translations = self._parse_translation_response(response, flat_texts)
            print(translations)

            idx = 0
            translated_groups: list[dict] = []

            for group in text_data:
                bubble = group.get("bubble", {})
                raw = group.get("text", "") or ""
                cleaned = raw.strip()

                if cleaned:
                    if idx < len(translations):
                        translated_text = translations[idx]
                    else:
                        translated_text = raw
                    idx += 1
                    translated_groups.append(
                        {
                            "bubble": bubble,
                            "text": translated_text,
                            "translation_confidence": 0.9,
                        }
                    )
                else:
                    translated_groups.append(
                        {
                            "bubble": bubble,
                            "text": raw,
                            "translation_confidence": 0.0,
                        }
                    )

            return translated_groups

        except Exception as e:
            raise e


    def _build_translation_prompt(
        self,
        texts: list[str],
        target_lang: str,
        context: Context
        ) -> str:
        title = context.title if context and context.title else "(unknown title)"
        alt_titles = context.alt_titles if context and context.alt_titles else []
        description = context.description if context and context.description else ""
        tags = context.tags if context and context.tags else []
        demographic = ", ".join(context.publication_demographic) if context and context.publication_demographic else "unspecified"
        year = str(context.year) if context and context.year else "unspecified"

        context_meta = {
            "title": title,
            "altTitles": alt_titles,
            "description": description,
            "tags": tags,
            "publicationDemographic": demographic,
            "originalYear": year,
        }

        prompt = f"""
            You are a professional manga translator/localizer.

            SERIES CONTEXT (use for disambiguation and tone):
            {json.dumps(context_meta, ensure_ascii=False, indent=2)}

            TASK:
            Translate each of the following speech-bubble texts from to {target_lang}.

            IMPORTANT REQUIREMENTS:
            1. Preserve story context, emotions, and intent.
            2. Use series context (description, tags, demographic) to resolve ambiguous terms.
            3. Adapt cultural references, idioms, and honorifics into natural English unless they carry essential nuance.
            4. Make translations short and clean enough to fit in speech bubbles.
            5. Render sound effects with natural English onomatopoeia only when meaningful (e.g., action, impact, emotion).
            6. Do not omit or invent information — stay faithful to the text.
            7. Output the same number of entries, in the same order.

            INPUT (ordered list of source bubble texts):
            {json.dumps(texts, ensure_ascii=False, indent=2)}

            OUTPUT FORMAT (STRICT):
            Return only a JSON array of translated strings in order.
            Example: ["translated text 1", "translated text 2"]

            TRANSLATION:
        """.strip()

        return prompt


    def _translate_with_retry(self, model, prompt: str) -> str:
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
                    time.sleep(self.retry_delay * (2**attempt))

        raise last_error

    def _parse_translation_response(
        self, response: str, original_texts: list[str]
    ) -> list[str]:
        try:
            response_clean = response.strip()

            if response_clean.startswith("```json"):
                response_clean = response_clean.strip("`")
                response_clean = response_clean.replace("json", "", 1).strip()
            elif response_clean.startswith("```"):
                response_clean = response_clean.strip("`").strip()

            parsed = json.loads(response_clean)

            if not isinstance(parsed, list):
                raise ValueError("Response is not a list")

            translations = []
            for i, src in enumerate(original_texts):
                if i < len(parsed):
                    translations.append(str(parsed[i]))
                else:
                    translations.append(src)

            return translations

        except Exception as e:
            raise e
