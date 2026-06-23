"""
Application settings loaded from environment variables and .env file.
Uses pydantic-settings for automatic .env discovery and validation.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """AgentKB-Diag application settings.

    All values can be overridden via environment variables or a .env file
    placed in the backend/ directory.
    """

    # LLM configuration
    llm_provider: str = "openai"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 2048

    # Agent pipeline
    agent_default_mode: str = "rule"  # "rule" or "llm"
    agent_max_retries: int = 3
    agent_retry_delay_seconds: float = 1.0

    # Paths (relative to project root)
    workspace_dir: str = "workspace"
    data_raw_dir: str = "data/raw"
    wiki_dir: str = "workspace/wiki"
    index_dir: str = "workspace/index"
    rounds_dir: str = "workspace/rounds"
    log_file: str = "workspace/wiki/log.md"

    # Semantic Scholar API (optional)
    semantic_scholar_api_key: str = ""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


# Module-level singleton
settings = Settings()
