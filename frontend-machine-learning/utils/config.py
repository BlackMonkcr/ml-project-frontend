"""
Configuración del sistema ML integrado
"""

from pathlib import Path
import os

def get_base_path():
    """Detectar automáticamente el directorio base de la aplicación"""
    # Obtener el directorio donde está este archivo (utils/)
    current_file = Path(__file__).resolve()
    utils_dir = current_file.parent

    # El directorio base debería ser el padre de utils/
    base_dir = utils_dir.parent

    # Lista de posibles ubicaciones base, en orden de prioridad
    possible_bases = [
        base_dir,  # Directorio normal (frontend-machine-learning/)
        Path.cwd(),  # Directorio de trabajo actual
        Path.cwd() / "frontend-machine-learning",  # Si está en la raíz del repo
        utils_dir.parent.parent / "frontend-machine-learning",  # Navegación desde utils
        Path("/mount/src/ml-project-frontend/frontend-machine-learning"),  # Streamlit Cloud específico
    ]

    # También buscar en el directorio padre si contiene frontend-machine-learning
    cwd = Path.cwd()
    if "frontend-machine-learning" not in str(cwd):
        for parent in [cwd.parent, cwd.parent.parent]:
            frontend_subdir = parent / "frontend-machine-learning"
            if frontend_subdir.exists():
                possible_bases.append(frontend_subdir)

    # Verificar cada candidato
    for candidate in possible_bases:
        if not candidate.exists():
            continue

        model_path = candidate / "saved_models"
        data_path = candidate / "data"

        # Verificar si tiene la estructura esperada
        if model_path.exists() and data_path.exists():
            print(f"🔍 Base path detectado (completo): {candidate}")
            return candidate
        elif model_path.exists() or data_path.exists():
            print(f"🔍 Base path detectado (parcial): {candidate}")
            return candidate

    # Fallback al directorio base calculado
    print(f"⚠️ Usando fallback path: {base_dir}")
    print(f"   CWD actual: {Path.cwd()}")
    print(f"   Archivo actual: {current_file}")
    return base_dir

# Configuración de paths con detección automática
BASE_PATH = get_base_path()
MODEL_DIR = BASE_PATH / "saved_models"
MODEL_FILE = "explicit_lyrics_classifier.pkl"
MODEL_PATH = MODEL_DIR / MODEL_FILE

# Path del dataset
DATA_PATH = BASE_PATH / "data" / "spotify_dataset_sin_duplicados_4.csv"

# Configuración de ML
CACHE_ENABLED = True
MAX_BATCH_SIZE = 100
DEFAULT_CONFIDENCE_THRESHOLD = 0.6

# Palabras explícitas para análisis de fallback
EXPLICIT_KEYWORDS = {
    'fuck', 'shit', 'bitch', 'damn', 'hell', 'ass', 'bastard',
    'cock', 'dick', 'pussy', 'whore', 'slut', 'motherfucker',
    'fucking', 'fucked', 'nigga', 'nigger', 'cunt', 'faggot'
}

# Configuración de logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Mensajes de error comunes
ERROR_MESSAGES = {
    "MODEL_NOT_AVAILABLE": "Modelo no disponible",
    "EMPTY_LYRICS": "Las letras no pueden estar vacías",
    "BATCH_TOO_LARGE": f"Máximo {MAX_BATCH_SIZE} letras por lote",
    "PREDICTION_ERROR": "Error en predicción",
    "ANALYSIS_ERROR": "Error en análisis de palabras"
}

def get_model_info():
    """Obtener información del modelo local"""
    return {
        "model_path": str(MODEL_PATH),
        "model_exists": MODEL_PATH.exists(),
        "model_size": MODEL_PATH.stat().st_size if MODEL_PATH.exists() else 0,
        "model_dir": str(MODEL_DIR),
        "cache_enabled": CACHE_ENABLED
    }
