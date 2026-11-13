#!/bin/bash

# cleaned up using Gemini.
set -e

echo "=================================================="
echo " Setting up the WSL env as we work on Windows"
echo "=================================================="

ENV_BASE="$HOME/Info-h420/assignement3"
VENV_DIR="$ENV_BASE/airflow_venv"
AIRFLOW_HOME_DIR="$ENV_BASE/airflow_home"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[1/8] Setting up project directories..."
mkdir -p "$ENV_BASE"
mkdir -p "$AIRFLOW_HOME_DIR"
mkdir -p "$PROJECT_DIR/dags"
mkdir -p "$PROJECT_DIR/data"
mkdir -p "$PROJECT_DIR/templates"

# Create symlinks
if [ ! -e "$ENV_BASE/repo" ]; then
    ln -s "$PROJECT_DIR" "$ENV_BASE/repo"
    echo "  Created symlink: $ENV_BASE/repo -> $PROJECT_DIR"
fi

if [ ! -e "$AIRFLOW_HOME_DIR/dags" ]; then
    ln -s "$PROJECT_DIR/dags" "$AIRFLOW_HOME_DIR/dags"
    echo "  Created symlink: $AIRFLOW_HOME_DIR/dags -> $PROJECT_DIR/dags"
fi

echo "[2/8] Checking configuration file..."
if [ ! -f "$PROJECT_DIR/.env" ] && [ -f "$PROJECT_DIR/example.env" ]; then
    cp "$PROJECT_DIR/example.env" "$PROJECT_DIR/.env"
    echo "  Created .env from example.env (please review settings in .env)"
else
    echo "  [OK] .env file already present."
fi

echo "[3/8] Ensuring Python 3.12 virtual environment..."
if [ -d "$VENV_DIR" ] && [ ! -f "$VENV_DIR/bin/activate" ]; then
    rm -rf "$VENV_DIR"
fi

if [ ! -f "$VENV_DIR/bin/activate" ]; then
    python3.12 -m venv "$VENV_DIR"
    echo "  Virtual environment created at $VENV_DIR"
else
    echo "  Virtual environment already exists at $VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "[4/8] Upgrading pip, setuptools, wheel..."
pip install --upgrade pip setuptools wheel --quiet

echo "[5/8] Installing Apache Airflow 3.3.2 and Project Dependencies..."
AIRFLOW_VERSION="3.3.2"
PYTHON_VERSION=$(python3 --version | cut -d " " -f 2 | cut -d "." -f 1-2)
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}" --quiet
pip install pymupdf4llm openai requests python-dotenv jinja2 --quiet

echo "[6/8] Initializing Airflow Metadata Database and Credentials..."
export AIRFLOW_HOME="$AIRFLOW_HOME_DIR"
export AIRFLOW__CORE__LOAD_EXAMPLES=False
airflow db migrate >/dev/null 2>&1 || true

# Set default credentials for admin user
PASS_FILE="$AIRFLOW_HOME_DIR/simple_auth_manager_passwords.json.generated"
echo '{"admin": "admin"}' > "$PASS_FILE"
chmod 600 "$PASS_FILE"
if [ -d "$HOME/airflow" ]; then
    echo '{"admin": "admin"}' > "$HOME/airflow/simple_auth_manager_passwords.json.generated" 2>/dev/null || true
fi
echo "  Configured default Airflow admin credentials (username: admin, password: admin)"

echo "[7/8] Checking Ollama service and model..."
if command -v ollama >/dev/null 2>&1; then
    echo "  [OK] Ollama is installed."
    if ! ollama list 2>/dev/null | grep -q "llama3.2"; then
        echo "  Pulling llama3.2:1b model in Ollama..."
        ollama pull llama3.2:1b || true
    else
        echo "  [OK] llama3.2 model is ready in Ollama."
    fi
else
    echo "  [i] Ollama not found. Install via: curl -fsSL https://ollama.com/install.sh | sh"
fi

echo "[8/8] Verifying python imports..."
python3 -c "
import airflow
import pymupdf4llm
import openai
import requests
import sqlite3
import dotenv
import jinja2
print('  [OK] All core libraries imported successfully.')
print(f'  [OK] Airflow version: {airflow.__version__}')
"

echo "=================================================="
echo " Setup completed successfully."
echo " Next steps:"
echo "   1. source activate_env.sh"
echo "   2. airflow standalone"
echo "=================================================="
