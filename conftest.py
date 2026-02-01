"""Pytest configuration with OpenAI key management."""
import os
import pytest

# Try to load .env files for testing (optional)
try:
    from dotenv import load_dotenv
    load_dotenv("/Users/benreich/agentprinter/.env.test")
    load_dotenv("/Users/benreich/agentprinter/.env")
except ImportError:
    pass  # dotenv not installed, use environment variables

def pytest_configure(config):
    """Configure pytest with environment variables."""
    os.environ.setdefault("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))

@pytest.fixture
def openai_key():
    """Fixture providing OpenAI API key, skip test if not available."""
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key or key == "sk-your-key-here":
        pytest.skip("OPENAI_API_KEY not configured")
    return key

@pytest.fixture
def openai_model():
    """Fixture providing OpenAI model name."""
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")
