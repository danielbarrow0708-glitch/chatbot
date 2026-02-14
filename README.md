# Text Optimizer Demo

A minimal Flask demo that sends text to a DeepSeek-compatible LLM API and returns a rewritten version.

## Requirements

- Python 3.10+

## Setup

1. Create a virtual environment and install dependencies.
2. Set the environment variable DEEPSEEK_API_KEY.
3. Optional: set DEEPSEEK_API_BASE, DEEPSEEK_MODEL, and MAX_INPUT_CHARS if needed.

## Run (development)

- python app.py

## Run (production)

- gunicorn app:app

## Notes

- The app exposes POST /optimize for the frontend.
- Errors are returned as JSON and shown on the page.
