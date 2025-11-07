#!/usr/bin/env bash
set -euo pipefail

# Activa el venv
source ~/jupyter_env/bin/activate
echo "Usando entorno virtual: $VIRTUAL_ENV"

# Directorio donde están tus notebooks
NB_DIR=~/jupyter_env/trabajo/pipeline

# Salidas temporales (los notebooks ya suben CSV/markers a GCS por su cuenta)
TS=$(date +%s)
OUT1="/tmp/demandadoyresultadogcp_out_${TS}.ipynb"
OUT2="/tmp/etiquetavertexgcp_out_${TS}.ipynb"

# Ejecuta ambos notebooks (si aceptan parámetros, añade --parameters ...)
papermill "$NB_DIR/demandadoyresultadogcp.ipynb" "$OUT1"
papermill "$NB_DIR/etiquetavertexgcp.ipynb"      "$OUT2"

echo "Batch OK: $OUT1 y $OUT2"
