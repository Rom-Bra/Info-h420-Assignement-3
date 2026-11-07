
#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_DIR="$HOME/Info-h420/assignement3"

source "$ENV_DIR/airflow_venv/bin/activate"
export AIRFLOW_HOME="$ENV_DIR/airflow_home"

echo "  Environnement activé"
echo "   Code du projet : $PROJECT_DIR"
echo "   Venv           : $ENV_DIR/airflow_venv"
echo "   AIRFLOW_HOME   : $AIRFLOW_HOME"
