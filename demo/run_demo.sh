#!/bin/bash

echo "═══════════════════════════════════════════════════════════"
echo "🚛 LogiQ AI - Demo Completo"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar que estamos en el directorio correcto
if [ ! -f "setup.sh" ]; then
    echo "❌ Error: Ejecutar desde el directorio raíz del proyecto"
    exit 1
fi

# Activar entorno virtual
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Entorno virtual no encontrado. Ejecutando setup...${NC}"
    ./setup.sh
fi

source venv/bin/activate

# Cargar variables de entorno
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Generar y cargar datos si no existen
if [ ! -f "data/logiq.db" ]; then
    echo -e "${BLUE}📊 Generando datos simulados...${NC}"
    python3 scripts/generate_data.py
    
    echo ""
    echo -e "${BLUE}🔄 Cargando datos en SQLite...${NC}"
    python3 scripts/load_data.py
else
    echo -e "${GREEN}✅ Base de datos ya existe${NC}"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🎯 Queries Demo para Probar"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "1. ¿Qué camión tuvo más alertas de temperatura en la última semana?"
echo "2. Promedio de consumo por marca de camión en los últimos 30 días"
echo "3. ¿Cuántos viajes finalizados hubo ayer?"
echo "4. Mostrar las 10 últimas alertas críticas"
echo "5. Lista de camiones actualmente en mantenimiento"
echo "6. Top 5 rutas con más retrasos"
echo "7. ¿Cuál es el conductor con más kilómetros recorridos este mes?"
echo "8. Alertas de velocidad excesiva en la última semana"
echo "9. Camiones con nivel de combustible bajo (< 20%)"
echo "10. Viajes más largos por región"
echo ""

# Ejemplos de curl para probar la API
echo "═══════════════════════════════════════════════════════════"
echo "🔧 Comandos cURL para Probar la API"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "# Health check:"
echo "curl http://localhost:8000/health"
echo ""
echo "# Query ejemplo 1:"
echo 'curl -X POST http://localhost:8000/query \\'
echo '  -H "Content-Type: application/json" \\'
echo '  -d '"'"'{"user": "demo", "nl": "Lista de camiones en mantenimiento"}'"'"
echo ""
echo "# Query ejemplo 2:"
echo 'curl -X POST http://localhost:8000/query \\'
echo '  -H "Content-Type: application/json" \\'
echo '  -d '"'"'{"user": "demo", "nl": "Mostrar las últimas alertas críticas"}'"'"
echo ""
echo "# Ver logs:"
echo "curl http://localhost:8000/logs?limit=5"
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "🚀 Iniciando Servicios"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo -e "${BLUE}Backend API se iniciará en: http://localhost:8000${NC}"
echo -e "${BLUE}Frontend UI se iniciará en: http://localhost:8501${NC}"
echo ""
echo "Presiona Ctrl+C para detener los servicios"
echo ""

# Preguntar si quiere iniciar los servicios
read -p "¿Iniciar backend y frontend? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Iniciar backend en background
    echo -e "${BLUE}🔧 Iniciando backend...${NC}"
    cd backend
    uvicorn app:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    # Esperar a que el backend esté listo
    echo "Esperando a que el backend esté listo..."
    sleep 3
    
    # Verificar que el backend está corriendo
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}✅ Backend corriendo en http://localhost:8000${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend puede tardar unos segundos en estar listo${NC}"
    fi
    
    # Iniciar frontend
    echo ""
    echo -e "${BLUE}🎨 Iniciando frontend...${NC}"
    cd frontend
    streamlit run streamlit_app.py --server.port 8501 &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo -e "${GREEN}✅ Demo iniciado exitosamente!${NC}"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "📡 Backend API: http://localhost:8000"
    echo "🎨 Frontend UI: http://localhost:8501"
    echo "📊 API Docs: http://localhost:8000/docs"
    echo ""
    echo "PIDs: Backend=$BACKEND_PID, Frontend=$FRONTEND_PID"
    echo ""
    echo "Para detener:"
    echo "  kill $BACKEND_PID $FRONTEND_PID"
    echo ""
    
    # Mantener el script corriendo
    wait
else
    echo ""
    echo "Demo cancelado. Para iniciar manualmente:"
    echo "  Terminal 1: ./run_backend.sh"
    echo "  Terminal 2: ./run_frontend.sh"
fi
