#!/bin/bash

# Script de inicio conjunto para producción
# Inicia tanto la API como Streamlit

set -e

echo "🚀 Iniciando ML Project - Modo Producción"

# Configuración
API_DIR="ml-project-models"
FRONTEND_DIR="frontend-machine-learning"
API_PORT="8000"
STREAMLIT_PORT="8501"

# Verificar directorios
if [ ! -d "$API_DIR" ]; then
    echo "❌ Error: Directorio $API_DIR no encontrado"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ Error: Directorio $FRONTEND_DIR no encontrado"
    exit 1
fi

# Función para cleanup al salir
cleanup() {
    echo "🛑 Deteniendo servicios..."
    jobs -p | xargs -r kill
    exit
}
trap cleanup SIGINT SIGTERM

# 1. Preparar entorno para API
echo "📦 Configurando entorno API..."
cd "$API_DIR"

# Crear venv si no existe
if [ ! -d "venv_api" ]; then
    python3 -m venv venv_api
fi

# Activar venv e instalar dependencias
source venv_api/bin/activate
pip install --upgrade pip
pip install -r requirements_api.txt

# Verificar modelo
if [ ! -f "saved_models/explicit_lyrics_classifier.pkl" ]; then
    echo "⚠️  Modelo no encontrado, intentando entrenar..."
    if [ -f "train_api_model.py" ]; then
        python train_api_model.py
    else
        echo "❌ No se puede entrenar modelo automáticamente"
        exit 1
    fi
fi

# 2. Iniciar API en background
echo "🔧 Iniciando API en puerto $API_PORT..."
uvicorn api:app --host 0.0.0.0 --port $API_PORT &
API_PID=$!

# Esperar que API inicie
sleep 10

# Verificar que API está corriendo
if ! curl -f http://localhost:$API_PORT/health > /dev/null 2>&1; then
    echo "❌ API no pudo iniciarse correctamente"
    kill $API_PID 2>/dev/null || true
    exit 1
fi

echo "✅ API iniciada exitosamente en http://localhost:$API_PORT"

# 3. Preparar entorno para Streamlit
cd "../$FRONTEND_DIR"

# Instalar dependencias de frontend si es necesario
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# 4. Iniciar Streamlit
echo "🎨 Iniciando Streamlit en puerto $STREAMLIT_PORT..."
export API_URL="http://localhost:$API_PORT"

streamlit run app.py \
    --server.port $STREAMLIT_PORT \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false &

STREAMLIT_PID=$!

# 5. Mostrar información
echo ""
echo "✅ Servicios iniciados exitosamente!"
echo "🌐 Frontend: http://localhost:$STREAMLIT_PORT"
echo "📡 API: http://localhost:$API_PORT"
echo "📖 API Docs: http://localhost:$API_PORT/docs"
echo ""
echo "💡 Presiona Ctrl+C para detener todos los servicios"

# 6. Esperar hasta interrupción
wait
