# INFO-H420 Assignment 3: Research Paper Processing Pipeline with Apache Airflow

This repository contains the complete solution for **INFO-H420 Assignment 3 (Management of Data Science and Business Workflows)**.

The project implements an automated, scheduled data pipeline orchestrating research paper ingestion using **Apache Airflow 3**, converting incoming PDF documents to Markdown with **PyMuPDF4LLM**, extracting structured JSON metadata using a local **Ollama LLM** (`llama3.2`), persisting records into a local **SQLite database**, regenerating a static searchable/filterable HTML study library using an external **Jinja2 HTML template**, and dispatching real-time notifications to **Discord**.

---

## Architecture and Repository Structure

The architecture separates cloud-synced storage (Google Drive) from local databases and pipelines to prevent locking conflicts and file churn:

```
Google Drive (Synced Folder):
└── ResearchLibrary/
    ├── papers/                 <- Drop research PDFs here (e.g., sample_paper.pdf)
    └── output/
        └── index.html          <- Auto-regenerated static study library web page

Local Repository:
├── dags/
│   ├── paper_pipeline.py       <- Main Airflow DAG (scan -> process -> generate_html)
│   └── pipeline/               <- Each task has its own dedicated subscript
│       ├── __init__.py         <- Package exports
│       ├── config.py           <- Central environment loader and configuration class
│       ├── db.py               <- SQLite schema management and data access functions
│       ├── pdf_parser.py       <- PDF to Markdown conversion (PyMuPDF4LLM)
│       ├── llm.py              <- Ask the local LLM to summarize (single retry)
│       ├── html_builder.py     <- Fill the template with relevant data
│       └── notifier.py         <- Discord webhook notification sender
├── templates/
│   └── index.html              <- Template for HTML file
├── data/                       <- Local SQLite storage (papers.db, git-ignored)
├── example.env                 <- Documented environment template to copy as .env
├── activate_env.sh             <- Shell script to activate environment and launch Airflow
├── setup_wsl_env.sh            <- As in Windows, set everything up on WSL
├── Assignment 3.pdf            <- Assigment
├── .gitignore                  <- Git ignore rules (.env, data/*.db, logs/, caches)
└── README.md                   <- This file.
```

---

## Requirements

- **Operating System**: Windows 10/11 with WSL2 (Ubuntu 22.04 LTS) or native Linux.
- **Python**: Version 3.12 (with `python3.12-venv` and `python3.12-dev`).
- **Workflow Orchestration**: Apache Airflow 3.3.2 running in standalone mode.
- **PDF Conversion**: `pymupdf4llm` (PyMuPDF4LLM) for structured Markdown extraction.
- **Local LLM Serving**: Ollama running locally with the `llama3.2:1b` (or `llama3.2`) model (OpenAI-compatible REST API on port 11434).
- **LLM Client**: `openai` Python SDK (communicating with Ollama endpoint in structured JSON format).
- **Database**: SQLite3 (`data/papers.db`, kept strictly local outside cloud synchronization).
- **Templating**: `jinja2` (used by `html_builder.py` to compile `templates/index.html` into `output/index.html`).
- **Alerts**: Discord incoming webhook integration via HTTP POST.

---

## Configuration (`.env` and `example.env`)

For security and environment independence, the active `.env` file is excluded from Git tracking via `.gitignore`.
See `example.env`.

### Setting up `.env`

Copy `example.env` to `.env`:

```bash
cp example.env .env
```

Open `.env` and adjust the variables to your local paths.

---

## Automated Setup (WSL2 / Ubuntu)

An automated script `setup_wsl_env.sh` prepares the entire environment:

1. Open your WSL2 Ubuntu terminal:
   ```bash
   cd /mnt/c/Users/your_user/PycharmProjects/ba-3/Info-h420-Assignement-3
   ```

2. Make sure the script is executable and run it:
   ```bash
   chmod +x setup_wsl_env.sh activate_env.sh
   ./setup_wsl_env.sh
   ```

The script performs the following actions:
- Creates required local folders (`data/`, `templates/`, `dags/`).
- Initializes a Python 3.12 virtual environment at `~/Info-h420/assignement3/airflow_venv`.
- Installs Apache Airflow 3.3.2 with official constraints, along with `pymupdf4llm`, `openai`, `requests`, `python-dotenv`, and `jinja2`.
- Initializes the Airflow metadata database (`airflow db migrate`).
- Generates default admin credentials (`admin` / `admin`).
- Checks if Ollama is available and ensures `llama3.2` is pulled.
- Creates `.env` from `example.env` if no `.env` file exists.

---

## Running the Pipeline

### 1. Start Ollama

Ensure Ollama is running and the model is present:

```bash
ollama run llama3.2:1b "hello"
```

Ollama runs its API server on `http://127.0.0.1:11434`.

### 2. Launch Airflow

In WSL or plain Linux:

```bash
source activate_env.sh
airflow standalone
```

The standalone process runs the Airflow Webserver, Scheduler, Triggerer, and DAG Processor.

### 3. Access the Airflow Web UI

Open your browser and navigate to:
- **URL**: [http://localhost:8080](http://localhost:8080)
- **Username**: `admin`
- **Password**: `admin`

### Known Issue

If you get errors like `command not found` right after cloning the project and running a script, it means the files were corrupted by Windows during the download. To fix this:

```bash
sudo apt install dos2unix -y
dos2unix setup_wsl_env.sh activate_env.sh .env
```

Then run `source activate_env.sh` again.
---

## Airflow DAG Workflow Details

The DAG `paper_pipeline` is defined in [dags/paper_pipeline.py](dags/paper_pipeline.py). It runs on a scheduled interval (every 1 minute) or on-demand:

```
[scan_new_papers] -> [process_paper_batch] -> [generate_library_html]
```

1. **`scan_new_papers`**:
   - Inspects `PAPERS_DIR` for `.pdf` files.
   - Queries `papers.db` to identify filenames not yet processed.
   - If no new files are found, subsequent tasks complete immediately without extra work.

2. **`process_paper_batch`**:
   - For each unprocessed PDF:
     1. Converts PDF to Markdown using PyMuPDF4LLM.
     2. Calls Ollama (`llama3.2`) with structured prompt requesting JSON:
        ```json
        {
          "title": "Paper title",
          "summary": "A short summary of the paper.",
          "keywords": ["keyword one", "keyword two"],
          "category": "Data Engineering"
        }
        ```
     3. Parses and validates the JSON output (retries once if parsing fails).
     4. Saves metadata into `papers.db` (`filename`, `title`, `summary`, `keywords`, `category`, `processed_at`).
     5. Dispatches an embed notification to the Discord webhook.

3. **`generate_library_html`**:
   - Queries all records from `papers.db` in descending order of ingestion date.
   - Loads the external template from [templates/index.html](templates/index.html).
   - Renders the static HTML page into `OUTPUT_DIR/index.html`.
---

## Manual Verification and CLI Commands

```bash
source activate_env.sh

# List all discovered DAGs
airflow dags list

# List tasks in the pipeline
airflow tasks list paper_pipeline

# Test task execution locally
airflow tasks test paper_pipeline scan_new_papers 2026-01-01
airflow tasks test paper_pipeline generate_library_html 2026-01-01

# Manually trigger a full DAG run
airflow dags trigger paper_pipeline
```

---

## Viewing the Output Study Library

Once papers are processed, open the generated file in your browser:

- Relative path in GDrive: `ResearchLibrary\output\index.html`
