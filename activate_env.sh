#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_DIR="$HOME/Info-h420/assignement3"

if [ ! -d "$ENV_DIR/airflow_venv" ]; then
    echo "Virtual environment not found at $ENV_DIR/airflow_venv!"
    echo "Running setup_wsl_env.sh..."
    bash "$PROJECT_DIR/setup_wsl_env.sh"
fi

source "$ENV_DIR/airflow_venv/bin/activate"
export AIRFLOW_HOME="$ENV_DIR/airflow_home"
export AIRFLOW__CORE__DAGS_FOLDER="$PROJECT_DIR/dags"
export AIRFLOW__CORE__LOAD_EXAMPLES=False

# Ensure Google Drive is mounted in WSL if G: drive exists
if [ ! -d "/mnt/g/Mon Drive" ]; then
    sudo mkdir -p /mnt/g 2>/dev/null || true
    sudo mount -t drvfs G: /mnt/g 2>/dev/null || true
fi

# Load .env variables if present
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a
    source "$PROJECT_DIR/.env"
    set +a
fi

# Ensure symlink for dags exists
if [ ! -e "$AIRFLOW_HOME/dags" ]; then
    ln -s "$PROJECT_DIR/dags" "$AIRFLOW_HOME/dags"
fi

echo "=================================================="
echo "  INFO-H420 Assignment 3 - Environment Activated"
echo "=================================================="
echo "  Project Code   : $PROJECT_DIR"
echo "  Python / Venv  : $(which python3)"
echo "  AIRFLOW_HOME   : $AIRFLOW_HOME"
echo "  DAGs Folder    : $PROJECT_DIR/dags"
echo "  Webserver UI   : http://localhost:8080"
echo "--------------------------------------------------"
echo "  Quick Commands:"
echo "    airflow standalone    # Start Airflow UI and scheduler"
echo "    airflow dags list     # List discovered DAGs"
echo "=================================================="
