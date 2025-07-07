#!/bin/bash

# Script para iniciar la API del backend
# Este script maneja el entorno virtual y ejecuta la API FastAPI

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuración
API_DIR="../ml-project-models"
API_FILE="api.py"
VENV_DIR="$API_DIR/venv_api"
REQUIREMENTS_FILE="$API_DIR/requirements_api.txt"
HOST="0.0.0.0"
PORT="8000"

echo -e "${GREEN}🚀 Iniciando servidor de API para ML Project${NC}"

# Verificar que estamos en el directorio correcto
if [ ! -d "$API_DIR" ]; then
    echo -e "${RED}❌ Error: Directorio $API_DIR no encontrado${NC}"
    echo "Asegúrate de ejecutar este script desde frontend-machine-learning/"
    exit 1
fi

# Cambiar al directorio de la API
cd "$API_DIR"

# Crear entorno virtual si no existe
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}📦 Creando entorno virtual...${NC}"
    python3 -m venv "$VENV_DIR"
fi

# Activar entorno virtual
echo -e "${YELLOW}🔧 Activando entorno virtual...${NC}"
source "$VENV_DIR/bin/activate"

# Actualizar pip
echo -e "${YELLOW}📋 Actualizando pip...${NC}"
pip install --upgrade pip

# Instalar dependencias
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo -e "${YELLOW}📚 Instalando dependencias desde $REQUIREMENTS_FILE...${NC}"
    pip install -r "$REQUIREMENTS_FILE"
else
    echo -e "${YELLOW}📚 Instalando dependencias básicas...${NC}"
    pip install fastapi uvicorn pandas scikit-learn pickle-mixin numpy python-multipart
fi

# Verificar que el archivo de API existe
if [ ! -f "$API_FILE" ]; then
    echo -e "${RED}❌ Error: $API_FILE no encontrado${NC}"
    exit 1
fi

# Verificar que el modelo existe
if [ ! -f "saved_models/explicit_lyrics_classifier.pkl" ]; then
    echo -e "${YELLOW}⚠️  Modelo no encontrado en saved_models/explicit_lyrics_classifier.pkl${NC}"
    echo -e "${YELLOW}🔧 Intentando entrenar modelo...${NC}"

    if [ -f "train_api_model.py" ]; then
        python train_api_model.py
    else
        echo -e "${RED}❌ No se puede entrenar el modelo automáticamente${NC}"
        echo "Por favor entrena el modelo manualmente antes de continuar"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Todo listo! Iniciando servidor...${NC}"
echo -e "${GREEN}🌐 API disponible en: http://localhost:$PORT${NC}"
echo -e "${GREEN}📖 Documentación: http://localhost:$PORT/docs${NC}"
echo -e "${YELLOW}💡 Presiona Ctrl+C para detener el servidor${NC}"
echo ""

# Iniciar el servidor
uvicorn "$API_FILE:app" --host "$HOST" --port "$PORT" --reload
