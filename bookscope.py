import base64
import io
import json
import os
import re
import tempfile
from typing import Any

import pandas as pd
import requests
from PIL import Image

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency is present in normal installs
    load_dotenv = None

if load_dotenv:
    load_dotenv()


SCAN_COLUMNS = ["title", "author", "confidence", "source", "notes"]
ENRICHED_COLUMNS = [
    "title",
    "author",
    "confidence",
    "isbn",
    "first_publish_year",
    "publisher",
    "subjects",
    "info_url",
    "lookup_status",
    "notes",
]

VISION_PROMPT = """Extract visible book spines from this shelf image.

Return only valid JSON in this shape:
{
  "books": [
    {
      "title": "best visible title guess",
      "author": "best visible author guess or Unknown",
      "confidence": 0.0,
      "notes": "short uncertainty note"
    }
  ]
}

Rules:
- Read upside-down, rotated, partial, and low-contrast spines when possible.
- Use Unknown for missing authors.
- Confidence must be between 0 and 1.
- Include uncertain but plausible books rather than hiding them.
- Do not invent books that are not visible.
"""

DEMO_RECORDS = [
    {
        "title": "The Guns of August",
        "author": "Barbara W. Tuchman",
        "confidence": 0.74,
        "source": "demo",
        "notes": "Demo row. Configure HF_TOKEN and BOOKSCOPE_HF_MODEL for live shelf scans.",
    },
    {
        "title": "Team of Rivals",
        "author": "Doris Kearns Goodwin",
        "confidence": 0.68,
        "source": "demo",
        "notes": "Demo row for the end-to-end table and enrichment flow.",
    },
]


def scan_shelf_image(image: Image.Image | None) -> tuple[pd.DataFrame, str]:
    if image is None:
        return _empty_scan_frame(), "Add a shelf image to scan."

    if _demo_mode_enabled():
        return pd.DataFrame(DEMO_RECORDS, columns=SCAN_COLUMNS), _demo_status()

    try:
        raw_response = _call_hf_vision_model(image)
        records = _parse_books(raw_response)
    except Exception as exc:  # pragma: no cover - provider failures depend on remote APIs
        records = []
        raw_response = ""
        provider_error = str(exc)
    else:
        provider_error = ""

    if not records:
        fallback = pd.DataFrame(DEMO_RECORDS, columns=SCAN_COLUMNS)
        status = "Live scan did not return parseable books."
        if provider_error:
            status = f"{status} Provider error: {provider_error}"
        elif raw_response:
            status = f"{status} Raw response was not valid Bookscope JSON."
        return fallback, status

    return pd.DataFrame(records, columns=SCAN_COLUMNS), f"Found {len(records)} visible book candidates."


def enrich_books(table: Any) -> tuple[pd.DataFrame, str]:
    records = _table_to_records(table)
    if not records:
        return pd.DataFrame(columns=ENRICHED_COLUMNS), "No book rows to enrich."

    enriched = [_enrich_one(record) for record in records]
    matches = sum(1 for row in enriched if row.get("lookup_status") == "matched")
    return pd.DataFrame(enriched, columns=ENRICHED_COLUMNS), f"Enriched {matches} of {len(enriched)} rows."


def _demo_mode_enabled() -> bool:
    value = os.getenv("BOOKSCOPE_DEMO_MODE", "").strip().lower()
    if value in {"0", "false", "no", "off"}:
        return False
    has_inference_model = bool(os.getenv("HF_TOKEN") and os.getenv("BOOKSCOPE_HF_MODEL"))
    has_gradio_space = bool(os.getenv("BOOKSCOPE_GRADIO_SPACE"))
    return not (has_inference_model or has_gradio_space)


def _demo_status() -> str:
    return (
        "Demo mode is active. Add either HF_TOKEN + BOOKSCOPE_HF_MODEL or "
        "BOOKSCOPE_GRADIO_SPACE, then set BOOKSCOPE_DEMO_MODE=false for live MiniCPM-V scans."
    )


def _call_hf_vision_model(image: Image.Image) -> str:
    if os.getenv("BOOKSCOPE_GRADIO_SPACE"):
        return _call_hf_gradio_space(image)

    token = os.environ["HF_TOKEN"]
    model = os.environ["BOOKSCOPE_HF_MODEL"]
    provider = os.getenv("BOOKSCOPE_HF_PROVIDER") or None

    from huggingface_hub import InferenceClient

    client_kwargs: dict[str, Any] = {"model": model, "token": token}
    if provider:
        client_kwargs["provider"] = provider

    try:
        client = InferenceClient(**client_kwargs)
    except TypeError:
        client_kwargs.pop("provider", None)
        client = InferenceClient(**client_kwargs)

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": VISION_PROMPT},
                {"type": "image_url", "image_url": {"url": _image_to_data_url(image)}},
            ],
        }
    ]

    if hasattr(client, "chat_completion"):
        response = client.chat_completion(
            messages=messages,
            max_tokens=1200,
            temperature=0.1,
        )
    else:  # pragma: no cover - compatibility branch for newer OpenAI-style clients
        response = client.chat.completions.create(
            messages=messages,
            max_tokens=1200,
            temperature=0.1,
        )

    return _response_content(response)


def _call_hf_gradio_space(image: Image.Image) -> str:
    from gradio_client import Client, handle_file

    space = os.environ["BOOKSCOPE_GRADIO_SPACE"]
    api_name = os.getenv("BOOKSCOPE_GRADIO_API_NAME", "/predict")
    input_order = os.getenv("BOOKSCOPE_GRADIO_INPUT_ORDER", "image_prompt").strip().lower()
    token = os.getenv("HF_TOKEN") or None

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
        temp_path = temp_file.name
        image.convert("RGB").save(temp_file, format="JPEG", quality=88)

    try:
        client = Client(space, hf_token=token)
        image_file = handle_file(temp_path)
        if input_order == "prompt_image":
            result = client.predict(VISION_PROMPT, image_file, api_name=api_name)
        elif input_order == "image":
            result = client.predict(image_file, api_name=api_name)
        else:
            result = client.predict(image_file, VISION_PROMPT, api_name=api_name)
    finally:
        try:
            os.unlink(temp_path)
        except OSError:
            pass

    return _response_content(result)


def _response_content(response: Any) -> str:
    if isinstance(response, str):
        return response
    if isinstance(response, dict):
        return (
            response.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
    choices = getattr(response, "choices", [])
    if choices:
        message = getattr(choices[0], "message", None)
        content = getattr(message, "content", None)
        if content is not None:
            return str(content)
    return str(response)


def _image_to_data_url(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, format="JPEG", quality=88)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def _parse_books(raw_response: str) -> list[dict[str, Any]]:
    payload = _json_from_text(raw_response)
    if isinstance(payload, list):
        books = payload
    else:
        books = payload.get("books", []) if isinstance(payload, dict) else []

    records = []
    for book in books:
        if not isinstance(book, dict):
            continue
        record = _normalize_scan_record(book)
        if record["title"]:
            records.append(record)
    return records


def _json_from_text(text: str) -> Any:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    match = re.search(r"(\{.*\}|\[.*\])", cleaned, flags=re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return {}


def _normalize_scan_record(book: dict[str, Any]) -> dict[str, Any]:
    title = str(book.get("title") or "").strip()
    author = str(book.get("author") or book.get("authors") or "Unknown").strip()
    notes = str(book.get("notes") or book.get("note") or "").strip()
    confidence = _coerce_confidence(book.get("confidence"))
    return {
        "title": title,
        "author": author or "Unknown",
        "confidence": confidence,
        "source": "vision",
        "notes": notes,
    }


def _coerce_confidence(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, round(number, 2)))


def _table_to_records(table: Any) -> list[dict[str, Any]]:
    if table is None:
        return []
    if isinstance(table, pd.DataFrame):
        frame = table.copy()
    else:
        frame = pd.DataFrame(table)
    if frame.empty:
        return []
    frame = frame.dropna(how="all")
    if frame.empty:
        return []
    return frame.to_dict(orient="records")


def _enrich_one(record: dict[str, Any]) -> dict[str, Any]:
    base = {
        "title": _clean_cell(record.get("title")),
        "author": _clean_cell(record.get("author")) or "Unknown",
        "confidence": _coerce_confidence(record.get("confidence")),
        "isbn": "",
        "first_publish_year": "",
        "publisher": "",
        "subjects": "",
        "info_url": "",
        "lookup_status": "not_found",
        "notes": _clean_cell(record.get("notes")),
    }
    if not base["title"]:
        base["lookup_status"] = "missing_title"
        return base

    try:
        match = _open_library_match(base["title"], base["author"])
    except requests.RequestException as exc:
        base["lookup_status"] = f"lookup_error: {exc.__class__.__name__}"
        return base

    if not match:
        return base

    isbn = _first(match.get("isbn")) or _isbn_from_editions(match.get("key"))
    base.update(
        {
            "title": match.get("title") or base["title"],
            "author": _first(match.get("author_name")) or base["author"],
            "isbn": isbn,
            "first_publish_year": match.get("first_publish_year") or "",
            "publisher": _first(match.get("publisher")),
            "subjects": ", ".join((match.get("subject") or [])[:4]),
            "info_url": f"https://openlibrary.org{match.get('key', '')}",
            "lookup_status": "matched" if isbn else "matched_no_isbn",
        }
    )
    return base


def _open_library_match(title: str, author: str) -> dict[str, Any] | None:
    params = {"title": title, "limit": 5}
    if author and author != "Unknown":
        params["author"] = author
    response = requests.get(
        "https://openlibrary.org/search.json",
        params=params,
        timeout=8,
    )
    response.raise_for_status()
    docs = response.json().get("docs", [])
    if not docs:
        return None
    return next((doc for doc in docs if doc.get("isbn")), docs[0])


def _isbn_from_editions(work_key: Any) -> str:
    if not work_key:
        return ""
    try:
        response = requests.get(
            f"https://openlibrary.org{work_key}/editions.json",
            params={"limit": 10},
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException:
        return ""

    for edition in response.json().get("entries", []):
        isbn = _first(edition.get("isbn_13")) or _first(edition.get("isbn_10"))
        if isbn:
            return isbn
    return ""


def _first(value: Any) -> str:
    if isinstance(value, list):
        return str(value[0]) if value else ""
    return str(value) if value else ""


def _clean_cell(value: Any) -> str:
    if value is None:
        return ""
    if pd.isna(value):
        return ""
    return str(value).strip()


def _empty_scan_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=SCAN_COLUMNS)
