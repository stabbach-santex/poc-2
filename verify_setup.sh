#!/bin/bash

echo "═══════════════════════════════════════════════════════════"
echo "🔍 LogiQ AI - Verificación de Setup"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

# Función para verificar archivo
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} $1"
    else
        echo -e "${RED}❌${NC} $1 - FALTA"
        ((ERRORS++))
    fi
}

# Función para verificar directorio
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅${NC} $1/"
    else
        echo -e "${RED}❌${NC} $1/ - FALTA"
        ((ERRORS++))
    fi
}

# Función para verificar comando
check_command() {
    if command -v $1 &> /dev/null; then
        VERSION=$($1 --version 2>&1 | head -n1)
        echo -e "${GREEN}✅${NC} $1 - $VERSION"
    else
        echo -e "${RED}❌${NC} $1 - NO INSTALADO"
        ((ERRORS++))
    fi
}

echo "📋 Verificando Requisitos del Sistema"
echo "─────────────────────────────────────"
check_command python3
check_command pip
check_command curl
echo ""

echo "📁 Verificando Estructura de Directorios"
echo "─────────────────────────────────────────"
check_dir "data"
check_dir "adapters"
check_dir "mappings"
check_dir "backend"
check_dir "backend/lib"
check_dir "frontend"
check_dir "scripts"
check_dir "tests"
check_dir "demo"
check_dir "slides"
check_dir "logs"
echo ""

echo "📄 Verificando Archivos Principales"
echo "────────────────────────────────────"
check_file "README.md"
check_file "QUICKSTART.md"
check_file "SUMMARY.md"
check_file "TODO.md"
check_file "API.md"
check_file "PROJECT_OVERVIEW.md"
check_file "requirements.txt"
check_file "setup.sh"
check_file "run_backend.sh"
check_file "run_frontend.sh"
check_file ".env.example"
check_file "LICENSE"
check_file "pytest.ini"
check_file "Dockerfile"
check_file "docker-compose.yml"
echo ""

echo "🔧 Verificando Scripts"
echo "──────────────────────"
check_file "scripts/generate_data.py"
check_file "scripts/load_data.py"
check_file "demo/run_demo.sh"
check_file "demo/demo_script.md"
echo ""

echo "🐍 Verificando Código Backend"
echo "──────────────────────────────"
check_file "backend/app.py"
check_file "backend/__init__.py"
check_file "backend/lib/__init__.py"
check_file "backend/lib/validate_sql.py"
check_file "backend/lib/gemini_client.py"
echo ""

echo "🎨 Verificando Frontend"
echo "───────────────────────"
check_file "frontend/streamlit_app.py"
echo ""

echo "🔄 Verificando Adapters"
echo "───────────────────────"
check_file "adapters/__init__.py"
check_file "adapters/adapter_base.py"
check_file "adapters/tera_adapter.py"
check_file "adapters/cloudfleet_adapter.py"
check_file "adapters/scania_adapter.py"
check_file "adapters/keeper_adapter.py"
echo ""

echo "📋 Verificando Mappings"
echo "───────────────────────"
check_file "mappings/tera_mapping.yaml"
check_file "mappings/cloudfleet_mapping.yaml"
check_file "mappings/scania_mapping.yaml"
check_file "mappings/keeper_mapping.yaml"
echo ""

echo "🧪 Verificando Tests"
echo "────────────────────"
check_file "tests/__init__.py"
check_file "tests/test_adapters.py"
check_file "tests/test_sql_validator.py"
check_file "tests/test_end_to_end.py"
echo ""

echo "📊 Verificando Slides"
echo "─────────────────────"
check_file "slides/pitch.md"
echo ""

# Verificar permisos de ejecución
echo "🔐 Verificando Permisos de Ejecución"
echo "─────────────────────────────────────"
if [ -x "setup.sh" ]; then
    echo -e "${GREEN}✅${NC} setup.sh es ejecutable"
else
    echo -e "${YELLOW}⚠️${NC}  setup.sh no es ejecutable - ejecutar: chmod +x setup.sh"
    ((WARNINGS++))
fi

if [ -x "run_backend.sh" ]; then
    echo -e "${GREEN}✅${NC} run_backend.sh es ejecutable"
else
    echo -e "${YELLOW}⚠️${NC}  run_backend.sh no es ejecutable - ejecutar: chmod +x run_backend.sh"
    ((WARNINGS++))
fi

if [ -x "run_frontend.sh" ]; then
    echo -e "${GREEN}✅${NC} run_frontend.sh es ejecutable"
else
    echo -e "${YELLOW}⚠️${NC}  run_frontend.sh no es ejecutable - ejecutar: chmod +x run_frontend.sh"
    ((WARNINGS++))
fi

if [ -x "demo/run_demo.sh" ]; then
    echo -e "${GREEN}✅${NC} demo/run_demo.sh es ejecutable"
else
    echo -e "${YELLOW}⚠️${NC}  demo/run_demo.sh no es ejecutable - ejecutar: chmod +x demo/run_demo.sh"
    ((WARNINGS++))
fi
echo ""

# Verificar entorno virtual
echo "🐍 Verificando Entorno Virtual"
echo "───────────────────────────────"
if [ -d "venv" ]; then
    echo -e "${GREEN}✅${NC} Entorno virtual existe"
    
    # Verificar si está activado
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        echo -e "${GREEN}✅${NC} Entorno virtual activado"
    else
        echo -e "${YELLOW}⚠️${NC}  Entorno virtual no activado - ejecutar: source venv/bin/activate"
        ((WARNINGS++))
    fi
else
    echo -e "${YELLOW}⚠️${NC}  Entorno virtual no existe - ejecutar: ./setup.sh"
    ((WARNINGS++))
fi
echo ""

# Verificar .env
echo "⚙️  Verificando Configuración"
echo "─────────────────────────────"
if [ -f ".env" ]; then
    echo -e "${GREEN}✅${NC} Archivo .env existe"
    
    if grep -q "GEMINI_API_KEY=your_gemini_api_key_here" .env; then
        echo -e "${YELLOW}⚠️${NC}  API key no configurada (modo mock)"
        ((WARNINGS++))
    else
        echo -e "${GREEN}✅${NC} API key configurada"
    fi
else
    echo -e "${YELLOW}⚠️${NC}  Archivo .env no existe - se creará en setup"
    ((WARNINGS++))
fi
echo ""

# Verificar base de datos
echo "💾 Verificando Base de Datos"
echo "────────────────────────────"
if [ -f "data/logiq.db" ]; then
    SIZE=$(du -h data/logiq.db | cut -f1)
    echo -e "${GREEN}✅${NC} Base de datos existe (${SIZE})"
else
    echo -e "${YELLOW}⚠️${NC}  Base de datos no existe - se creará al ejecutar run_backend.sh"
    ((WARNINGS++))
fi
echo ""

# Resumen
echo "═══════════════════════════════════════════════════════════"
echo "📊 RESUMEN"
echo "═══════════════════════════════════════════════════════════"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ TODO PERFECTO!${NC}"
    echo ""
    echo "El proyecto está completamente configurado y listo para usar."
    echo ""
    echo "Próximos pasos:"
    echo "  1. ./setup.sh (si no lo has ejecutado)"
    echo "  2. ./run_backend.sh"
    echo "  3. ./run_frontend.sh (en otra terminal)"
    echo ""
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  ADVERTENCIAS: ${WARNINGS}${NC}"
    echo ""
    echo "El proyecto está funcional pero hay algunas advertencias."
    echo "Revisa los mensajes arriba para más detalles."
    echo ""
else
    echo -e "${RED}❌ ERRORES: ${ERRORS}${NC}"
    echo -e "${YELLOW}⚠️  ADVERTENCIAS: ${WARNINGS}${NC}"
    echo ""
    echo "Hay archivos o directorios faltantes."
    echo "Por favor revisa los mensajes arriba y corrige los errores."
    echo ""
fi

echo "═══════════════════════════════════════════════════════════"

exit $ERRORS
