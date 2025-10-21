#!/bin/bash

echo "🚀 LogiQ AI - Setup Script"
echo "=========================="

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar Python 3.10+
echo -e "${BLUE}Verificando Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado. Por favor instalar Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION encontrado"

# Crear entorno virtual
echo -e "${BLUE}Creando entorno virtual...${NC}"
python3 -m venv venv
source venv/bin/activate

# Actualizar pip
echo -e "${BLUE}Actualizando pip...${NC}"
pip install --upgrade pip

# Instalar dependencias
echo -e "${BLUE}Instalando dependencias...${NC}"
pip install fastapi uvicorn[standard] pandas sqlalchemy streamlit requests pytest pyyaml python-dotenv google-generativeai openai

# Crear estructura de directorios
echo -e "${BLUE}Creando estructura de directorios...${NC}"
mkdir -p data
mkdir -p adapters
mkdir -p mappings
mkdir -p backend/lib
mkdir -p frontend
mkdir -p tests
mkdir -p demo
mkdir -p slides
mkdir -p scripts
mkdir -p logs

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo -e "${BLUE}Creando archivo .env template...${NC}"
    cat > .env << EOF
# API Keys (configurar al menos una)
GEMINI_API_KEY=your_gemini_api_key_here
# OPENAI_API_KEY=your_openai_key_here

# BigQuery (opcional)
USE_BIGQUERY=false
# BQ_PROJECT=your-gcp-project
# BQ_DATASET=logiq_warehouse

# Configuración
PORT=8000
EOF
    echo "⚠️  Por favor configurar API keys en .env"
fi

# Crear .gitignore
echo -e "${BLUE}Creando .gitignore...${NC}"
cat > .gitignore << EOF
# Python
venv/
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
dist/
*.egg-info/

# Environment
.env
.env.local

# Database
*.db
*.sqlite
*.sqlite3

# Logs
logs/*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# BigQuery credentials
*.json
!mappings/*.json
EOF

echo ""
echo -e "${GREEN}✅ Setup completado!${NC}"
echo ""
echo "Próximos pasos:"
echo "1. Configurar API key en .env"
echo "2. Ejecutar: ./run_backend.sh"
echo "3. En otra terminal: ./run_frontend.sh"
echo ""
