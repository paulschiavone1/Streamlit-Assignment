"""Read configuration without printing credentials.

Order of lookup: Streamlit secrets (deployed app) -> environment / local .env file.
"""
import os
from pathlib import Path

from dotenv import load_dotenv


def _setting(name):
    """Return a setting from Streamlit secrets if present, else from the environment."""
    try:
        import streamlit as st
        if name in st.secrets:
            return str(st.secrets[name]).strip()
    except Exception:
        pass  # no secrets file locally; fall back to environment variables
    return os.getenv(name, "").strip()


def get_settings():
    load_dotenv(Path(__file__).with_name(".env"))
    url = _setting("SUPABASE_URL").rstrip("/")
    key = _setting("SUPABASE_SECRET_KEY")
    if not url.startswith("https://") or "YOUR_PROJECT" in url:
        raise ValueError("Set SUPABASE_URL to your project's HTTPS URL (in .env or Streamlit secrets).")
    if not key.startswith("sb_secret_"):
        raise ValueError("Set SUPABASE_SECRET_KEY to your own project's sb_secret_ key.")
    return url, key


def get_app_password():
    load_dotenv(Path(__file__).with_name(".env"))
    return _setting("APP_PASSWORD")

