# Hire an AI Manager (Streamlit)

A Streamlit chat app that uses the OpenAI Responses API + File Search against an existing Vector Store.

## Prerequisites

- Python 3.10+
- An OpenAI API key
- A Vector Store ID (already created in your OpenAI project)

## Setup

1. Create a virtual environment (recommended).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set environment variables (recommended via `.env` in the project root):

```bash
OPENAI_API_KEY=your_key_here
VECTOR_STORE_ID=vs_...
```

## Run

```bash
streamlit run app.py
```

## Notes

- `.env` is intentionally ignored by git.
- You can also provide `VECTOR_STORE_ID` via Streamlit Secrets, but `.streamlit/secrets.toml` is ignored by default.
