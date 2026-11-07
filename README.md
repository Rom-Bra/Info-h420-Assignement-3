# Airflow Paper Pipeline - Info-H420 Assignment 3

Airflow pipeline that watches a folder for new PDFs, converts them to
Markdown, asks a local LLM for a title/summary/keywords/category, saves
the metadata to SQLite, regenerates a static HTML page, and pings a
Discord webhook when a new paper is processed.

## Structure

Local Project/
- dags/              Airflow DAGs
- data/              Local SQLite db (papers.db), not synced
- activate_env.sh    Activates the venv and sets AIRFLOW_HOME
- README.md

The Python venv and AIRFLOW_HOME live outside this folder, on the WSL
(Linux) side. Venvs break under /mnt/c/... due to a WSL/Windows
symlink issue.

PDFs and the generated HTML page live in a separate folder synced via
Google Drive, outside this repo.

## Requirements

- WSL2 with Ubuntu
- Python 3.12 and python3.12-venv
- Google Drive for Desktop (for the synced papers/ folder)
- Ollama or LM Studio (for the local LLM)

## Setup (one-time, per machine)

1. Clone the repo into a folder named Local Project:

   git clone https://github.com/Rom-Bra/Info-h420-Assignement-3.git "Local Project"
   cd "Local Project"

2. Open a WSL terminal and set up a Python venv on the Linux side:

   mkdir -p ~/airflow-env
   python3 -m venv ~/airflow-env/airflow_venv
   source ~/airflow-env/airflow_venv/bin/activate
   pip install --upgrade pip
   AIRFLOW_VERSION=3.3.2
   PYTHON_VERSION=$(python3 --version | cut -d " " -f 2 | cut -d "." -f 1-2)
   CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
   pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"

3. Open activate_env.sh and point ENV_DIR to the venv you just created:

   ENV_DIR="$HOME/airflow-env"

## Running it (every time)

1. Open a WSL terminal
2. cd into the repo
3. source activate_env.sh
4. airflow standalone
5. Go to http://localhost:8080

