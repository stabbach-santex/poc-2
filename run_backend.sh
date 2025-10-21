#!/bin/bash

echo "🔧 LogiQ AI - Backend Setup & Launch"
echo "===================================="

# Activar entorno virtual
source venv/bin/activate

# Cargar variables de entorno
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Generar datos simulados si no existen
if [ ! -f data/logiq.db ]; then
    echo "📊 Generando datos simulados..."
    python3 scripts/generate_data.py
    
    echo "🔄 Cargando datos en SQLite..."
    python3 scripts/load_data.py
else
    echo "✅ Base de datos ya existe (data/logiq.db)"
fi

# Levantar servidor FastAPI
echo "🚀 Iniciando servidor FastAPI en puerto ${PORT:-8000}..."
cd backend
uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000} --reload
