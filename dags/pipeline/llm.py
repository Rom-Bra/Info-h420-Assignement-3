import json
import re
from typing import Any, Dict, Optional
from openai import OpenAI


def _clean_json_text(raw_text: str) -> str:
    """I couln't understand why some output were weird, it seems LLM
    returns sometimes a mardown like text we need to extract. Use of GEMINI to reach this conclusion."""
    text = raw_text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    return text


def _validate_metadata_dict(data: dict) -> bool:
    required = ["title", "summary", "keywords", "category"]
    for k in required:
        if k not in data or data[k] is None:
            return False
    if not isinstance(data["title"], str) or not data["title"].strip():
        return False
    if not isinstance(data["summary"], str) or not data["summary"].strip():
        return False
    if not isinstance(data["category"], str) or not data["category"].strip():
        return False
    if not isinstance(data["keywords"], (list, tuple)):
        return False
    return True


def extract_metadata_with_ollama(
    markdown_text: str,
    api_base: str = "http://localhost:11434/v1",
    api_key: str = "ollama",
    model: str = "llama3.2",
    max_input_chars: int = 4000,
) -> Dict[str, Any]:
    client = OpenAI(base_url=api_base, api_key=api_key)

    # Use first section of paper to capture title, abstract, introduction, and conclusion
    text_snippet = markdown_text[:max_input_chars] if len(markdown_text) > max_input_chars else markdown_text

    system_prompt = (
        "Extract metadata from the research paper text.\n"
        "Return ONLY a valid JSON object with the following exact keys:\n"
        "- title: The title of the paper (string)\n"
        "- summary: A short summary of the paper (2-4 sentences, string)\n"
        "- keywords: A list of 3-6 relevant keywords (list of strings)\n"
        "- category: Academic category, such as 'Data Engineering', 'Machine Learning', "
        "'Distributed Systems', 'Natural Language Processing', 'Security', etc. (string)"
    )

    user_prompt = f"Paper Content:\n\n{text_snippet}\n\nReturn JSON metadata:"

    def _query(retry_hint: str = "") -> Optional[Dict[str, Any]]:
        messages = [
            {"role": "system", "content": system_prompt + (f"\n\n{retry_hint}" if retry_hint else "")},
            {"role": "user", "content": user_prompt},
        ]
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=350,
            stop=["<|eot_id|>", "<|end_of_text|>", "<|im_end|>"],
        )
        content = response.choices[0].message.content or ""
        cleaned = _clean_json_text(content)
        parsed = json.loads(cleaned)
        if _validate_metadata_dict(parsed):
            cleaned_keywords = [str(k).strip() for k in parsed["keywords"] if str(k).strip()]
            return {
                "title": str(parsed["title"]).strip(),
                "summary": str(parsed["summary"]).strip(),
                "keywords": cleaned_keywords,
                "category": str(parsed["category"]).strip(),
            }
        return None

    # First attempt
    try:
        data = _query()
        if data:
            return data
    except Exception as first_err:
        print(f"First extraction failed: {first_err}.")

    # Single retry as required
    try:
        data = _query(
            retry_hint="Previous output failed validation. You MUST return strictly valid JSON with title, summary, keywords array, and category."
        )
        if data:
            return data
    except Exception as retry_err:
        print(f"Retry extraction failed: {retry_err}")

    raise ValueError("Failed to extract valid metadata JSON after retry.")
