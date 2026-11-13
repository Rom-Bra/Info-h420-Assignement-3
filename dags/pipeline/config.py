import os
from dataclasses import dataclass
from dotenv import load_dotenv

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_ENV_PATH = os.path.join(_PROJECT_ROOT, ".env")
if os.path.isfile(_ENV_PATH):
    load_dotenv(_ENV_PATH)


@dataclass(frozen=True)
class PipelineConfig:

    project_root: str = _PROJECT_ROOT
    papers_dir: str = os.getenv(
        "PAPERS_DIR",
        os.path.join(_PROJECT_ROOT, "..", "ResearchLibrary", "papers"),
    )
    output_dir: str = os.getenv(
        "OUTPUT_DIR",
        os.path.join(_PROJECT_ROOT, "..", "ResearchLibrary", "output"),
    )
    db_path: str = os.getenv(
        "DB_PATH",
        os.path.join(_PROJECT_ROOT, "data", "papers.db"),
    )
    template_path: str = os.getenv(
        "TEMPLATE_PATH",
        os.path.join(_PROJECT_ROOT, "templates", "index.html"),
    )
    llm_api_base: str = os.getenv("LLM_API_BASE", "http://localhost:11434/v1")
    llm_api_key: str = os.getenv("LLM_API_KEY", "ollama")
    llm_model: str = os.getenv("LLM_MODEL", "llama3.2:1b")
    discord_webhook_url: str = os.getenv("DISCORD_WEBHOOK_URL", "")


config = PipelineConfig()
