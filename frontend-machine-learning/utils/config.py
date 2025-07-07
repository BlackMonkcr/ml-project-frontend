"""
Configuración del sistema ML integrado
"""

from pathlib import Path

# Configuración de paths
MODEL_DIR = Path("saved_models")
MODEL_FILE = "explicit_lyrics_classifier.pkl"
MODEL_PATH = MODEL_DIR / MODEL_FILE

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
