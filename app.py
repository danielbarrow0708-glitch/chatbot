import logging
import os
from typing import Any, Dict

import requests
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv


API_KEY_ENV = "DEEPSEEK_API_KEY"
API_BASE_ENV = "DEEPSEEK_API_BASE"
MODEL_ENV = "DEEPSEEK_MODEL"
MAX_INPUT_CHARS_ENV = "MAX_INPUT_CHARS"

DEFAULT_API_BASE = "https://api.deepseek.com/v1"
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_MAX_INPUT_CHARS = 5000

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger("text_optimizer")

# Load environment variables from .env for local development.
load_dotenv()

app = Flask(__name__)


def build_messages(input_text: str) -> list[Dict[str, str]]:
    system_prompt = (
        "You are an experienced writer who rewrites content so it sounds natural, "
        "conversational, and believable while staying professional."
    )
    user_prompt = (
        "Rewrite the provided text to improve clarity, readability, and natural flow.\n\n"
        "Guidelines:\n"
        "- Write in a natural, spoken tone without being overly casual\n"
        "- Use many common abbreviations (aim for 15+ per paragraph)\n"
        "- Preferred abbreviations: u, ur, btw, imo, idk, tbh, w/, b/c, asap, tho\n"
        "- Include a missing end punctuation in at least one sentence\n"
        "- Avoid corporate buzzwords and generic marketing phrases\n"
        "- Avoid formulaic introductions (e.g., 'In today's digital world')\n"
        "- Do not use emojis\n"
        "- Avoid excessive bullet points\n"
        "- Avoid perfectly symmetrical paragraph structure\n"
        "- Vary sentence length naturally (mix short, medium, and long sentences)\n"
        "- Break predictable three-part patterns (e.g., 'builds trust, increases engagement, drives growth')\n"
        "- Use subtle conversational transitions when appropriate\n"
        "- Keep SEO keywords integrated naturally, not stacked\n"
        "- Do not sound overly polished or robotic\n"
        "- Keep the content professional but realistic\n"
        "- Avoid making every paragraph similar in length\n"
        "- Occasionally use contractions\n"
        "- Do not over-explain\n"
        "- Allow mild imperfection in rhythm\n"
        "- Keep meaning intact and do not add new facts\n"
        "- Use an occasional aside or self-correction if it fits (e.g., 'I mean', 'that said')\n"
        "- Let a few sentences be short or fragment-like when natural\n\n"
        "Make the writing feel like it came from a real person speaking to a reader.\n\n"
        f"Text to rewrite:\n\"\"\"\n{input_text}\n\"\"\"\n\n"
        "Return only the rewritten content, nothing else."
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def get_max_input_chars() -> int:
    raw_value = (os.getenv(MAX_INPUT_CHARS_ENV) or "").strip()
    if not raw_value:
        return DEFAULT_MAX_INPUT_CHARS
    try:
        value = int(raw_value)
    except ValueError:
        return DEFAULT_MAX_INPUT_CHARS
    return max(1, value)


def call_llm_api(input_text: str) -> str:
    api_key = os.getenv(API_KEY_ENV)
    if not api_key:
        raise RuntimeError("API credentials not configured.")

    api_base = os.getenv(API_BASE_ENV, DEFAULT_API_BASE).rstrip("/")
    model = os.getenv(MODEL_ENV, DEFAULT_MODEL)

    payload: Dict[str, Any] = {
        "model": model,
        "messages": build_messages(input_text),
        "temperature": 1.2,
        "top_p": 0.95,
        "frequency_penalty": 0.3,
        "presence_penalty": 0.2,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    url = f"{api_base}/chat/completions"
    logger.info("Sending request to LLM")
    response = requests.post(url, json=payload, headers=headers, timeout=45)
    response.raise_for_status()

    data = response.json()
    choices = data.get("choices", [])
    if not choices:
        raise RuntimeError("LLM response missing choices.")

    message = choices[0].get("message", {})
    content = message.get("content", "").strip()
    if not content:
        raise RuntimeError("LLM response was empty.")

    return content


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/optimize", methods=["POST"])
def optimize() -> Any:
    payload = request.get_json(silent=True) or {}
    text = (payload.get("text") or "").strip()

    if not text:
        return jsonify({"error": "Please enter some text."}), 400

    if len(text) > get_max_input_chars():
        return jsonify({"error": "Text is too long."}), 413

    try:
        optimized_text = call_llm_api(text)
        return jsonify({"result": optimized_text})
    except requests.RequestException as exc:
        logger.exception("LLM request failed")
        return jsonify({"error": "The optimization service is unavailable."}), 502
    except RuntimeError:
        logger.exception("Optimization failed")
        return jsonify({"error": "The optimization service is unavailable."}), 503
    except Exception:
        logger.exception("Unexpected error")
        return jsonify({"error": "Unexpected server error."}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
