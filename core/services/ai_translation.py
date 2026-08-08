import json
import os

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None


class TranslationBackendUnavailable(RuntimeError):
    pass


class TranslationValidationError(RuntimeError):
    pass


class BaseContentTranslationBackend:
    def is_available(self):
        return False

    def translate_payload(self, **kwargs):
        raise TranslationBackendUnavailable("No translation backend is configured.")


class OpenAIContentTranslationBackend(BaseContentTranslationBackend):
    def __init__(self):
        self.api_key = os.environ.get("JCW_OPENAI_API_KEY", "").strip() or os.environ.get("OPENAI_API_KEY", "").strip()
        self.model = os.environ.get("JCW_TRANSLATION_MODEL", "").strip() or os.environ.get("OPENAI_TRANSLATION_MODEL", "").strip() or "gpt-4.1-mini"
        self.client = OpenAI(api_key=self.api_key) if self.api_key and OpenAI else None

    def is_available(self):
        return bool(self.client)

    def translate_payload(self, *, block_label, site_name, source_language, target_language, source_payload, existing_target_payload, glossary_terms, fields=None):
        if not self.is_available():
            raise TranslationBackendUnavailable("OpenAI API key is not configured for content translation.")

        glossary_lines = []
        for term in glossary_terms:
            preferred = term.get("preferred_translation") or ""
            if term.get("never_translate"):
                glossary_lines.append(f"- {term['term']}: NEVER TRANSLATE")
            elif preferred:
                glossary_lines.append(f"- {term['term']}: prefer '{preferred}'")
            else:
                glossary_lines.append(f"- {term['term']}: preserve when already present")
        glossary_text = "\n".join(glossary_lines) if glossary_lines else "- none"
        target_variant = "European Portuguese (pt-PT)" if target_language == "pt" else target_language
        requested_fields = fields or list(source_payload.keys())
        instructions = f"""
Translate the JSON website content for Just Code Works.

Site identity: {site_name}
Page/section context: {block_label}
Source language: {source_language}
Target language: {target_variant}

Rules:
- Return JSON only.
- Return exactly these requested field keys and no others: {requested_fields}.
- Use natural target-country language.
- Preserve brand and product names.
- Preserve prices, URLs, HTML, and template variables.
- Preserve intentional formatting.
- Do not invent claims or add extra content.
- For Portuguese use European Portuguese.

Glossary:
{glossary_text}
""".strip()
        response = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": instructions}],
                },
                {
                    "role": "user",
                    "content": [{
                        "type": "input_text",
                        "text": json.dumps({"source_payload": source_payload, "existing_target_payload": existing_target_payload}, ensure_ascii=False),
                    }],
                },
            ],
        )
        raw_text = getattr(response, "output_text", "") or ""
        if not raw_text:
            raise TranslationValidationError("OpenAI returned an empty translation response.")
        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise TranslationValidationError("OpenAI translation response was not valid JSON.") from exc
        if not isinstance(data, dict):
            raise TranslationValidationError("OpenAI translation response must be a JSON object.")
        return data


def get_content_translation_backend():
    return OpenAIContentTranslationBackend()
