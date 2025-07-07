# 🚀 Guía de Despliegue para Streamlit

Esta guía te ayudará a resolver los dos problemas principales para el despliegue:

1. **Archivo CSV muy grande (211MB > 100MB límite GitHub)**
2. **Backend API requerido para funcionalidades completas**

## 📊 Problema 1: Dataset Grande

### Solución A: Git LFS (Recomendado para GitHub)

```bash
# 1. Instalar Git LFS
git lfs install

# 2. Configurar tracking (ya incluido en .gitattributes)
git lfs track "*.csv"
git lfs track "data/"

# 3. Agregar archivos
git add .gitattributes
git add data/spotify_dataset_sin_duplicados_4.csv
git commit -m "Add large dataset with LFS"
git push
```

### Solución B: Servicios en la Nube

#### Google Drive
1. Sube tu CSV a Google Drive
2. Haz click derecho → "Obtener enlace" → "Cualquiera con el enlace"
3. Copia el ID del archivo (entre `/d/` y `/view` en la URL)
4. En la app de Streamlit, usa la opción "Descargar desde la nube"

#### Dropbox
1. Sube tu CSV a Dropbox
2. Obtén enlace de descarga directa (reemplaza `dl=0` por `dl=1`)
3. Úsalo en la opción de descarga de la app

#### GitHub Releases
1. Ve a tu repositorio → Releases → Create new release
2. Sube el CSV como asset del release
3. Usa la URL de descarga directa

### Solución C: Dataset de Muestra
Para desarrollo/testing, la app puede generar un dataset de muestra con funcionalidad limitada.

## 🔗 Problema 2: Backend API

### Opción 1: Deployment Local (Desarrollo)

```bash
# 1. Iniciar API automáticamente
cd frontend-machine-learning/
./start_api.sh  # Linux/Mac
# o
start_api.bat   # Windows

# 2. Verificar que funciona
# API: http://localhost:8000
# Docs: http://localhost:8000/docs

# 3. Iniciar Streamlit
streamlit run app.py
```

### Opción 2: Deployment Conjunto (Producción)

#### Para Streamlit Cloud:

1. **Crear `requirements.txt` completo:**
```txt
streamlit
pandas
requests
numpy
scikit-learn
fastapi
uvicorn
python-multipart
```

2. **Crear script de inicio combinado (`startup.sh`):**
```bash
#!/bin/bash
# Iniciar API en background
cd ml-project-models/
uvicorn api:app --host 0.0.0.0 --port 8000 &
cd ../frontend-machine-learning/

# Esperar que API inicie
sleep 10

# Iniciar Streamlit
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

3. **Configurar Streamlit Cloud:**
   - Subir código a GitHub (con Git LFS para dataset)
   - En Streamlit Cloud, configurar startup command: `bash startup.sh`

#### Para Heroku:

1. **Crear `Procfile`:**
```
web: bash startup.sh
```

2. **Crear `runtime.txt`:**
```
python-3.9.18
```

3. **Configurar vars de entorno si es necesario**

#### Para Railway/Render:

1. **Railway:**
   - Conectar GitHub repo
   - Configurar start command: `bash startup.sh`
   - Añadir variables de entorno si es necesario

2. **Render:**
   - Similar a Railway
   - Configurar build y start commands

### Opción 3: APIs Separadas (Microservicios)

#### Backend API (FastAPI):
- Deploy en Heroku/Railway/Render
- Endpoint público (ej: `https://tu-api.herokuapp.com`)

#### Frontend (Streamlit):
- Deploy en Streamlit Cloud
- Configurar `API_BASE_URL` para apuntar al backend público

**Ejemplo de configuración:**
```python
# En utils/api_client.py
import os
API_BASE_URL = os.getenv("API_URL", "https://tu-api.herokuapp.com")
```

## 📁 Estructura Recomendada para Deploy

```
proyecto/
├── .gitattributes          # Para Git LFS
├── requirements.txt        # Dependencias completas
├── startup.sh             # Script de inicio conjunto
├── README.md              # Documentación
├── frontend-machine-learning/
│   ├── app.py             # App principal
│   ├── start_api.sh       # Script de API (desarrollo)
│   ├── utils/
│   │   ├── api_manager.py  # Manejo de API
│   │   ├── data_manager.py # Manejo de datasets
│   │   └── api_client.py   # Cliente API
│   └── data/
│       └── spotify_dataset_sin_duplicados_4.csv  # Con LFS
└── ml-project-models/
    ├── api.py             # FastAPI backend
    ├── requirements_api.txt
    └── saved_models/
        └── explicit_lyrics_classifier.pkl
```

## 🔧 Comandos de Desarrollo

```bash
# 1. Desarrollo local
cd frontend-machine-learning/
./start_api.sh           # Terminal 1: API
streamlit run app.py     # Terminal 2: Frontend

# 2. Testing conjunto
bash startup.sh          # Inicia ambos servicios

# 3. Solo frontend (sin funcionalidades de ML)
streamlit run app.py     # La app manejará la ausencia de API
```

## 🌐 URLs de Producción

- **Frontend Streamlit:** `https://tu-app.streamlit.app`
- **Backend API:** `https://tu-api.herokuapp.com`
- **Documentación API:** `https://tu-api.herokuapp.com/docs`

## 📝 Checklist de Deploy

### Pre-deploy:
- [ ] Dataset subido con Git LFS o configurado descarga
- [ ] Modelo ML entrenado y guardado
- [ ] Variables de entorno configuradas
- [ ] Requirements.txt completo
- [ ] Scripts de inicio creados

### Post-deploy:
- [ ] API funciona: `{api_url}/health`
- [ ] Frontend carga correctamente
- [ ] Dataset se descarga/carga automáticamente
- [ ] Funcionalidades de ML operativas
- [ ] Logs sin errores críticos

## 🐛 Solución de Problemas

### API no inicia:
```bash
# Verificar dependencias
pip install -r ml-project-models/requirements_api.txt

# Verificar modelo
ls ml-project-models/saved_models/

# Logs detallados
uvicorn api:app --log-level debug
```

### Dataset no carga:
- Verificar Git LFS: `git lfs ls-files`
- Verificar URLs de descarga
- Usar dataset de muestra para testing

### Streamlit Cloud issues:
- Verificar logs en el dashboard
- Reducir tamaño de dataset si es necesario
- Configurar secrets para URLs privadas
