"""
Automated workflow that:
1. Scans PAPERS_DIR for new unprocessed PDFs.
2. Converts PDF files to Markdown with PyMuPDF4LLM.
3. Calls local Ollama (llama3.2) to extract JSON metadata (title, summary, keywords, category).
4. Persists the metadata to local SQLite database (papers.db).
5. Regenerates a static searchable HTML library page (output/index.html).
6. Pings Discord webhook notification for newly added papers.
"""

from datetime import datetime, timedelta
import os
import sys

# Ensure the dags folder is on sys.path for modular imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from pipeline.config import config
from pipeline.db import (
    get_unprocessed_pdfs,
    init_db,
    save_paper_to_db,
)
from pipeline.pdf_parser import convert_pdf_to_markdown
from pipeline.llm import extract_metadata_with_ollama
from pipeline.html_builder import generate_html_page
from pipeline.notifier import notify_discord


def scan_new_papers_task(**context):
    init_db(config.db_path)
    unprocessed = get_unprocessed_pdfs(config.papers_dir, config.db_path)
    print(f"{len(unprocessed)} unprocessed PDF's in {config.papers_dir}")
    for filename in unprocessed:
        print(f"  - Pending: {filename}")
    return unprocessed


def process_paper_batch_task(**context):
    ti = context["ti"]
    unprocessed_files = ti.xcom_pull(task_ids="scan_new_papers") or []

    if not unprocessed_files:
        print("No papers")
        return 0

    processed_count = 0
    for filename in unprocessed_files:
        pdf_path = os.path.join(config.papers_dir, filename)
        print(f"Processing: {filename}")

        # Convert PDF to Markdown
        print("Converting PDF to Markdown")
        markdown_text = convert_pdf_to_markdown(pdf_path)

        # Extract metadata via Ollama
        print(f"Calling LLM model '{config.llm_model}' at {config.llm_api_base}")
        metadata = extract_metadata_with_ollama(
            markdown_text=markdown_text,
            api_base=config.llm_api_base,
            api_key=config.llm_api_key,
            model=config.llm_model,
        )
        print(f"Extracted metadata: Title='{metadata['title']}', Category='{metadata['category']}'")

        # Save to local SQLite database
        print(f"Saving to SQLite at {config.db_path}...")
        save_paper_to_db(config.db_path, filename, metadata)

        # Notify Discord
        metadata_with_filename = dict(metadata)
        metadata_with_filename["filename"] = filename
        notify_discord(config.discord_webhook_url, metadata_with_filename)

        # Update index.html immediately so the user can see progress in real time
        generate_html_page(config.db_path, config.output_dir)

        processed_count += 1
        print(f"Process finished: {filename}")

    return processed_count


def generate_library_html_task(**context):
    print(f"Generate HTML page {config.output_dir}")
    output_file = generate_html_page(config.db_path, config.output_dir)
    print(f"HTML available at: {output_file}")
    return output_file


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="paper_pipeline",
    default_args=default_args,
    description="Automated research paper study library pipeline",
    schedule=timedelta(minutes=1),
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["info-h420", "assignment3", "research"],
) as dag:

    scan_task = PythonOperator(
        task_id="scan_new_papers",
        python_callable=scan_new_papers_task,
    )

    process_task = PythonOperator(
        task_id="process_paper_batch",
        python_callable=process_paper_batch_task,
    )

    generate_html_task = PythonOperator(
        task_id="generate_library_html",
        python_callable=generate_library_html_task,
    )

    scan_task >> process_task >> generate_html_task
