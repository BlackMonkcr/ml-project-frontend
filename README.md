# 🎵 Music ML System - Proyecto de Machine Learning

## 📋 Descripción del Proyecto

Este es un sistema completo de Machine Learning para análisis de contenido explícito en letras de canciones, desarrollado como proyecto académico para el curso de Machine Learning en UTEC 2025-1.

### 🎯 Objetivos
- **Clasificación automática** de letras de canciones como explícitas o limpias
- **Análisis detallado** palabra por palabra para identificar contenido problemático  
- **Sistema de recomendaciones** basado en similaridad de letras usando Word2Vec
- **Búsqueda inteligente** con integración a Spotify API
- **Interfaz web moderna** para interacción con el usuario

### 🏗️ Arquitectura del Sistema

```
📁 Music ML System/
├── 🔙 Backend (FastAPI)     # API REST con modelos ML
├── 🖥️ Frontend (Streamlit)  # Interfaz web interactiva  
├── 🤖 ML Models             # Modelos entrenados y pipelines
├── 📊 Data                  # Dataset de Spotify (60K+ canciones)
└── 📚 Documentation         # Documentación y tutoriales
```

### 🛠️ Tecnologías Utilizadas
- **Backend**: FastAPI, Uvicorn, Pydantic
- **Frontend**: Streamlit, Pandas, Requests
- **ML**: Scikit-learn, NLTK, Gensim (Word2Vec)
- **Data**: Spotify Dataset (60K canciones), Spotipy API
- **Deploy**: Compatible con Docker, Heroku, AWS

---

## 🚀 Tutorial de Instalación y Ejecución

### ⚙️ Prerrequisitos

1. **Python 3.8+** instalado
2. **Git** para clonar el repositorio
3. **Cuenta de Spotify Developer** (opcional, para funciones avanzadas)

### 📥 Paso 1: Clonar y Preparar el Proyecto

```powershell
# Clonar el repositorio
git clone <tu-repo-url>
cd "Machine Learning\Proyecto"

# Verificar estructura
dir
```

### 📦 Paso 2: Configurar el Backend (API)

#### Opción A: Sistema Legacy (Recomendado para empezar)

```powershell
# Navegar al directorio del backend legacy
cd "ml-project-models"

# Crear entorno virtual
python -m venv venv_api
venv_api\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
python -c "import numpy, scipy, gensim, fastapi; print('✅ Dependencias OK')"
```

#### Opción B: Sistema Nuevo (Más moderno)

```powershell
# Navegar al directorio del backend nuevo
cd "music-ml-system\backend"

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 🚀 Paso 3: Ejecutar el Backend

#### Para Sistema Legacy:
```powershell
# Desde ml-project-models/ con entorno activado
python api.py

# O usando uvicorn
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

#### Para Sistema Nuevo:
```powershell
# Desde music-ml-system/backend/ con entorno activado
python -m app.main

# O usando uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### ✅ Verificar Backend
Abrir navegador en: `http://localhost:8000/docs` para ver la documentación automática de la API.

### 🖥️ Paso 4: Configurar el Frontend

#### Opción A: Frontend Legacy
```powershell
# Nueva terminal - navegar al frontend
cd "Frontend Machine Learning"

# Crear entorno virtual (opcional, puede usar el mismo)
python -m venv venv_frontend
venv_frontend\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

#### Opción B: Frontend Nuevo
```powershell
# Nueva terminal - navegar al frontend nuevo
cd "music-ml-system\frontend"

# Instalar dependencias
pip install -r requirements.txt
```

### 🎨 Paso 5: Ejecutar el Frontend

#### Para Frontend Legacy:
```powershell
# Desde Frontend Machine Learning/ con entorno activado
streamlit run app.py
```

#### Para Frontend Nuevo:
```powershell
# Desde music-ml-system/frontend/ con entorno activado
streamlit run main.py
```

### 🌐 Acceder a la Aplicación
El frontend se abrirá automáticamente en: `http://localhost:8501`

---

## 🔧 Configuración Avanzada

### 🎵 Spotify API (Opcional)

1. Ir a [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Crear una nueva aplicación
3. Obtener `Client ID` y `Client Secret`
4. Crear archivo `.env`:

```env
SPOTIFY_CLIENT_ID=tu_client_id_aqui
SPOTIFY_CLIENT_SECRET=tu_client_secret_aqui
```

### 📊 Dataset Personalizado

Para usar tu propio dataset:
1. Formato requerido: CSV con columnas `song`, `artist`, `text`, `explicit`
2. Colocar en `data/spotify_dataset_sin_duplicados_4.csv`
3. Reiniciar backend para recargar datos

---

## 🔍 Funcionalidades del Sistema

### 🎯 Análisis de Contenido Explícito
- **Clasificación binaria**: Explícito vs Limpio
- **Confianza del modelo**: Porcentaje de certeza
- **Análisis por palabras**: Identificación de términos problemáticos
- **Batch processing**: Análisis de múltiples canciones

### 🔎 Búsqueda Inteligente
- **Búsqueda por título/artista**: Con coincidencias parciales
- **Filtros por género**: Rock, Pop, Hip-Hop, etc.
- **Información de Spotify**: Covers, enlaces, popularidad
- **Paginación**: Navegación eficiente en resultados

### 💡 Sistema de Recomendaciones
- **Similaridad de letras**: Usando embeddings Word2Vec
- **Recomendaciones por artista**: Canciones similares del mismo artista
- **Filtros de contenido**: Solo explícitas, solo limpias, mixto
- **Scores de similaridad**: Métrica de qué tan parecidas son las canciones

---

## 📁 Estructura Detallada del Proyecto

### Sistema Legacy (`ml-project-models/`)
```
ml-project-models/
├── api.py                          # API FastAPI principal
├── models.py                       # Definición de modelos ML
├── recommendation_system.py        # Sistema de recomendaciones
├── requirements.txt                # Dependencias actualizadas
├── saved_models/                   # Modelos entrenados (.pkl)
│   └── explicit_lyrics_classifier.pkl
└── graphs/                         # Visualizaciones de evaluación
    ├── confusion_matrix-*.png
    └── detailed_confusion_matrix_*.png
```

### Sistema Nuevo (`music-ml-system/`)
```
music-ml-system/
├── backend/                        # API FastAPI modular
│   ├── app/
│   │   ├── main.py                # Punto de entrada
│   │   ├── core/config.py         # Configuración
│   │   ├── services/              # Lógica de negocio
│   │   └── routes/                # Endpoints de API
│   └── requirements.txt           # Dependencias backend
├── frontend/                      # Streamlit app
│   ├── main.py                    # App principal
│   ├── pages/                     # Páginas de la app
│   ├── utils/                     # Utilidades y helpers
│   └── requirements.txt           # Dependencias frontend
├── data/                          # Datasets y archivos de datos
├── models/                        # Modelos y pipelines ML
└── docs/                          # Documentación completa
```

---

## 🧪 Testing y Validación

### Verificar Funcionamiento Completo

1. **Test Backend**:
```powershell
# Con backend corriendo, probar endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d "{\"lyrics\":\"This is a test song\"}"
```

2. **Test Frontend**:
- Abrir `http://localhost:8501`
- Probar búsqueda de canciones
- Probar análisis de letras personalizadas
- Verificar conexión con backend

3. **Test ML Models**:
```python
# Verificar carga de modelos
python -c "
import pickle
model = pickle.load(open('saved_models/explicit_lyrics_classifier.pkl', 'rb'))
print('✅ Modelo cargado correctamente')
"
```

---

## 📋 Versiones y Compatibilidad

### Dependencias Principales

| Paquete | Versión | Uso en el Proyecto |
|---------|---------|-------------------|
| numpy | 1.24.3 | Operaciones matemáticas y compatibilidad pickle |
| scipy | 1.10.1 | Cálculos científicos para gensim |
| gensim | 4.3.2 | Modelos Word2Vec para recomendaciones |
| scikit-learn | 1.1.0-1.4.0 | Clasificadores ML (Naive Bayes, SVM, etc.) |
| fastapi | 0.95.0+ | Framework web para API REST |
| streamlit | 1.28.0+ | Framework web para frontend |
| spotipy | 2.22.0+ | Integración con Spotify API |

---

## 🐛 Resolución de Problemas Comunes

### ❌ Error: "Backend no conecta"
```powershell
# Verificar que FastAPI esté corriendo
curl http://localhost:8000/health

# Si no responde, verificar puerto y reiniciar
netstat -an | findstr 8000
```

### ❌ Error: "Modelo no carga (pickle)"
```powershell
# Verificar versión de numpy
python -c "import numpy; print(numpy.__version__)"

# Si no es 1.24.3, reinstalar
pip uninstall numpy -y
pip install numpy==1.24.3
```

### ❌ Error: "Dataset no encontrado"
1. Verificar que `spotify_dataset_sin_duplicados_4.csv` esté en la carpeta correcta
2. Verificar permisos de lectura del archivo
3. Verificar que el archivo no esté corrupto

### ❌ Error: "Streamlit no inicia"
```powershell
# Reinstalar streamlit
pip uninstall streamlit -y
pip install streamlit

# Verificar instalación
streamlit version
```

### ❌ Error: "Gensim/Word2Vec no funciona"
```powershell
# Verificar compatibilidad scipy
pip uninstall gensim scipy -y
pip install scipy==1.10.1 gensim==4.3.2
```

---

## 📈 Próximas Mejoras y Roadmap

### 🎯 Corto Plazo
- [ ] Optimización de velocidad de modelos
- [ ] Más filtros de búsqueda (año, duración, etc.)
- [ ] Exportación de resultados a CSV/JSON
- [ ] Modo batch para análisis masivo

### 🚀 Mediano Plazo  
- [ ] Análisis de sentimientos en letras
- [ ] Clasificación multi-clase (nivel de explicitud)
- [ ] Integración con más plataformas (YouTube, Apple Music)
- [ ] API de usuario con autenticación

### 💫 Largo Plazo
- [ ] Deploy en la nube (AWS/GCP/Azure)
- [ ] App móvil nativa
- [ ] Análisis en tiempo real de nuevas canciones
- [ ] Sistema de feedback de usuarios para mejorar modelos

---

## 👥 Información del Proyecto

### 🎓 Contexto Académico
- **Universidad**: UTEC (Universidad de Ingeniería y Tecnología)
- **Curso**: Machine Learning 2025-1
- **Objetivo**: Implementar un sistema completo de ML con clasificación y recomendaciones

### 📊 Métricas del Modelo
- **Dataset**: 60,000+ canciones de Spotify
- **Accuracy**: ~85% en clasificación explícito/limpio
- **Precision**: ~82% para contenido explícito
- **Recall**: ~88% para contenido explícito
- **F1-Score**: ~85% promedio

### 🔬 Algoritmos Utilizados
1. **Clasificación**: Naive Bayes, SVM, Logistic Regression
2. **Preprocesamiento**: TF-IDF, Stop Words, Stemming
3. **Recomendaciones**: Word2Vec + Cosine Similarity
4. **Búsqueda**: Fuzzy String Matching + Pandas

---

## 📄 Licencia y Uso

Este proyecto es de **uso académico** y está desarrollado con fines educativos. El dataset de Spotify se utiliza bajo términos de investigación académica.

### ⚖️ Términos de Uso
- ✅ Uso académico y educativo
- ✅ Modificación y mejora del código
- ✅ Presentación en contextos educativos
- ❌ Uso comercial sin autorización
- ❌ Redistribución del dataset original

### 🤝 Contribuciones
Las mejoras y sugerencias son bienvenidas. Para contribuir:
1. Fork del repositorio
2. Crear branch para nueva feature
3. Commit con mensaje descriptivo
4. Pull request con descripción detallada

---

## 📞 Soporte y Contacto

### 🆘 Obtener Ayuda
1. **Revisar documentación**: Este README y archivos en `/docs`
2. **Revisar issues conocidos**: Sección de resolución de problemas
3. **Verificar instalación**: Seguir pasos del tutorial paso a paso
4. **Logs del sistema**: Revisar mensajes de error en terminal

### 📧 Contacto
- **Proyecto académico**: Machine Learning UTEC 2025-1
- **Documentación adicional**: Ver carpeta `/docs`
- **Actualizaciones**: Revisar `REQUIREMENTS_UPDATE.md` para últimos cambios

---

## 🎉 ¡Listo para Usar!

Siguiendo este tutorial deberías tener:
- ✅ Backend FastAPI corriendo en puerto 8000
- ✅ Frontend Streamlit corriendo en puerto 8501  
- ✅ Modelos ML cargados y funcionando
- ✅ Sistema de recomendaciones activo
- ✅ Integración con Spotify (opcional)

**¡Disfruta explorando el mundo del análisis de letras con Machine Learning!** 🎵🤖
# ml-project-frontend
