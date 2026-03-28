"""Centralized configuration for the Supervisor Agent project."""

import os

from dotenv import load_dotenv

load_dotenv()

# --- LLM (Mistral) ---
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
SUPERVISOR_MODEL = os.getenv("SUPERVISOR_MODEL", "mistral-large-latest")
WORKER_MODEL = os.getenv("WORKER_MODEL", "mistral-small-latest")

# --- Langfuse ---
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

# --- Agent Names (single source of truth) ---
RESEARCH_AGENT = "research_expert"
MATH_AGENT = "math_expert"
WRITER_AGENT = "writer_expert"
SUPERVISOR_NAME = "supervisor"
