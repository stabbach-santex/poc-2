#!/bin/bash

echo "🎨 LogiQ AI - Frontend Launch"
echo "============================="

# Activar entorno virtual
source venv/bin/activate

# Cargar variables de entorno
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Levantar Streamlit
echo "🚀 Iniciando Streamlit UI..."
cd frontend
streamlit run streamlit_app.py --server.port 8501
