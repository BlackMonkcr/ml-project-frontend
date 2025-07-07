@echo off
REM Script para Windows para iniciar la API del backend

setlocal

REM Configuración
set API_DIR=..\ml-project-models
set API_FILE=api.py
set VENV_DIR=%API_DIR%\venv_api
set REQUIREMENTS_FILE=%API_DIR%\requirements_api.txt
set HOST=0.0.0.0
set PORT=8000

echo 🚀 Iniciando servidor de API para ML Project

REM Verificar que estamos en el directorio correcto
if not exist "%API_DIR%" (
    echo ❌ Error: Directorio %API_DIR% no encontrado
    echo Asegúrate de ejecutar este script desde frontend-machine-learning/
    exit /b 1
)

REM Cambiar al directorio de la API
cd "%API_DIR%"

REM Crear entorno virtual si no existe
if not exist "%VENV_DIR%" (
    echo 📦 Creando entorno virtual...
    python -m venv "%VENV_DIR%"
)

REM Activar entorno virtual
echo 🔧 Activando entorno virtual...
call "%VENV_DIR%\Scripts\activate"

REM Actualizar pip
echo 📋 Actualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias
if exist "%REQUIREMENTS_FILE%" (
    echo 📚 Instalando dependencias desde %REQUIREMENTS_FILE%...
    pip install -r "%REQUIREMENTS_FILE%"
) else (
    echo 📚 Instalando dependencias básicas...
    pip install fastapi uvicorn pandas scikit-learn pickle-mixin numpy python-multipart
)

REM Verificar que el archivo de API existe
if not exist "%API_FILE%" (
    echo ❌ Error: %API_FILE% no encontrado
    exit /b 1
)

REM Verificar que el modelo existe
if not exist "saved_models\explicit_lyrics_classifier.pkl" (
    echo ⚠️  Modelo no encontrado en saved_models\explicit_lyrics_classifier.pkl
    echo 🔧 Intentando entrenar modelo...

    if exist "train_api_model.py" (
        python train_api_model.py
    ) else (
        echo ❌ No se puede entrenar el modelo automáticamente
        echo Por favor entrena el modelo manualmente antes de continuar
        exit /b 1
    )
)

echo ✅ Todo listo! Iniciando servidor...
echo 🌐 API disponible en: http://localhost:%PORT%
echo 📖 Documentación: http://localhost:%PORT%/docs
echo 💡 Presiona Ctrl+C para detener el servidor
echo.

REM Iniciar el servidor
uvicorn %API_FILE%:app --host %HOST% --port %PORT% --reload
