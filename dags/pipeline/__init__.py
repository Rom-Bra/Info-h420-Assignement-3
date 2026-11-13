"""
INFO-H420 Assignment 3: Research Paper Pipeline Package
"""

from .config import PipelineConfig
from .db import init_db, get_processed_filenames, get_unprocessed_pdfs, save_paper_to_db, get_all_papers
from .pdf_parser import convert_pdf_to_markdown
from .llm import extract_metadata_with_ollama
from .html_builder import generate_html_page
from .notifier import notify_discord

__all__ = [
    "PipelineConfig",
    "init_db",
    "get_processed_filenames",
    "get_unprocessed_pdfs",
    "save_paper_to_db",
    "get_all_papers",
    "convert_pdf_to_markdown",
    "extract_metadata_with_ollama",
    "generate_html_page",
    "notify_discord",
]
