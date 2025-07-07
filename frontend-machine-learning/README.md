# 🎵 Explicit Lyrics Analyzer - Frontend

Frontend en Streamlit para el sistema de análisis de contenido explícito en letras de canciones.

## 🚀 Inicio Rápido

### 1. Instalar dependencias
```powershell
pip install -r requirements.txt
```

### 2. Ejecutar la aplicación
```powershell
streamlit run app.py
```

### 3. Abrir en navegador
La app se abrirá automáticamente en: `http://localhost:8501`

## ⚙️ Configuración

### Requisitos Previos
- **Backend API** corriendo en `http://localhost:8000`
- **Dataset** en `data/spotify_dataset_sin_duplicados_4.csv`
- **Python 3.8+** instalado

### Verificar Conexión con Backend
```bash
curl http://localhost:8000/health
```

## 🔍 Funcionalidades

### 🎯 Páginas Disponibles

1. **🔍 Buscar Canciones**
   - Búsqueda por título y/o artista
   - Filtros por género musical
   - Paginación de resultados
   - Información detallada de cada canción

2. **📝 Analizar Letras**
   - Análisis básico: explícito/limpio
   - Análisis detallado: palabra por palabra
   - Resaltado de términos problemáticos
   - Métricas de confianza del modelo

3. **💡 Sugerencias** (En desarrollo)
   - Sistema de recomendaciones
   - Filtros avanzados

### 🎨 Características de UI

- **Interfaz moderna** con cards responsivas
- **Navegación intuitiva** por sidebar
- **Resaltado visual** de palabras explícitas
- **Métricas de confianza** con colores:
  - 🟢 Alta (>80%): "Muy seguro"
  - 🟡 Media (60-80%): "Moderadamente seguro"
  - 🔴 Baja (<60%): "Poco seguro"

## 📁 Estructura

```
Frontend Machine Learning/
├── app.py                 # Aplicación principal
├── requirements.txt       # Dependencias
├── data/                  # Dataset local
│   └── spotify_dataset_sin_duplicados_4.csv
├── pages/                 # Páginas de la aplicación
│   ├── search_songs.py    # 🔍 Búsqueda
│   ├── analyze_lyrics.py  # 📝 Análisis
│   └── suggestions.py     # 💡 Sugerencias
└── utils/                 # Utilidades
    ├── api_client.py      # Cliente API
    └── data_manager.py    # Gestor de datos
```

## 🔧 Configuración Avanzada

### Variables de Entorno
```env
API_BASE_URL=http://localhost:8000
DATASET_PATH=data/spotify_dataset_sin_duplicados_4.csv
```

### Personalización
- **API URL**: Modificar en `utils/api_client.py`
- **Dataset**: Cambiar ruta en `utils/data_manager.py`
- **Estilos**: Personalizar CSS en `app.py`

## � Resolución de Problemas

### ❌ "API no conecta"
1. Verificar que FastAPI esté corriendo: `curl http://localhost:8000/health`
2. Verificar puerto 8000 libre: `netstat -an | findstr 8000`
3. Revisar firewall/antivirus

### ❌ "Dataset no carga"
1. Verificar archivo en `data/spotify_dataset_sin_duplicados_4.csv`
2. Verificar permisos de lectura
3. Verificar formato CSV correcto

### ❌ "Streamlit no inicia"
```powershell
pip uninstall streamlit -y
pip install streamlit
streamlit version
```

## 📊 Dataset Requerido

### Columnas Necesarias
- `Artist(s)` → Artista(s)
- `song` → Título de la canción
- `text` → Letras completas
- `Genre` → Género musical
- `Explicit` → Clasificación (Yes/No)

### Formato CSV
```csv
Artist(s),song,text,Genre,Explicit
"Drake","God's Plan","Yeah, they wishin'...",Hip-Hop,No
"Eminem","Lose Yourself","Look, if you had...",Hip-Hop,Yes
```

## 🚀 Para Desarrolladores

### Añadir Nueva Página
1. Crear archivo en `pages/nueva_pagina.py`
2. Implementar función `show()`
3. Añadir navegación en `app.py`

### Modificar API Client
```python
# utils/api_client.py
API_BASE_URL = "http://localhost:8000"  # Cambiar URL si es necesario
```

### Personalizar Estilos
```python
# app.py - Añadir CSS personalizado
st.markdown("""
<style>
/* Tu CSS aquí */
</style>
""", unsafe_allow_html=True)
```

## 📈 Próximas Mejoras

- [ ] Sistema de recomendaciones completo
- [ ] Filtros avanzados (año, duración)
- [ ] Exportación de resultados
- [ ] Modo oscuro/claro
- [ ] Historial de búsquedas
- [ ] Cache mejorado

---

**💡 Tip**: Para mejores resultados, asegúrate de que tanto el frontend como el backend estén corriendo antes de usar la aplicación.

Ver **[README principal](../README.md)** para documentación completa del proyecto.
