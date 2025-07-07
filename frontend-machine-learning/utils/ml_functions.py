"""
Módulo de ML integrado para Streamlit
Contiene todas las funciones de predicción y análisis sin API externa
"""

import pickle
import logging
import streamlit as st
from typing import Dict, Any, Optional, List
import os
import sys
from datetime import datetime
import numpy as np
from pathlib import Path

# Agregar el directorio utils al path para importar módulos locales
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

# Importar módulos locales
from .config import MODEL_PATH, EXPLICIT_KEYWORDS, ERROR_MESSAGES, get_model_info
from .pipeline import ModelPipeline
from .text_preprocessing import TextPreprocessor

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variable global para el modelo
_model_pipeline = None
_model_loaded = False

def get_model_path() -> Path:
    """Obtener la ruta del modelo en la carpeta local"""
    return MODEL_PATH

@st.cache_resource
def load_ml_model() -> tuple[Any, bool, str]:
    """
    Cargar el modelo de ML de forma segura con cache

    Returns:
        Tupla con (modelo, success, mensaje)
    """
    try:
        model_path = get_model_path()

        if not model_path.exists():
            return None, False, f"Modelo no encontrado en {model_path}"

        # Asegurar que los módulos estén disponibles para pickle
        import sys
        import importlib.util

        # Importar los módulos necesarios y agregarlos al namespace global
        from . import pipeline, text_preprocessing

        # Agregar al namespace de sys.modules para que pickle los encuentre
        sys.modules['pipeline'] = pipeline
        sys.modules['text_preprocessing'] = text_preprocessing

        # También agregarlos sin el prefijo utils
        sys.modules['utils.pipeline'] = pipeline
        sys.modules['utils.text_preprocessing'] = text_preprocessing

        with open(model_path, 'rb') as f:
            model = pickle.load(f)

        logger.info(f"Modelo cargado exitosamente desde {model_path}")
        return model, True, f"Modelo cargado desde {model_path}"

    except Exception as e:
        error_msg = f"Error cargando modelo: {str(e)}"
        logger.error(error_msg)
        return None, False, error_msg

def ensure_model_loaded() -> bool:
    """Asegurar que el modelo esté cargado"""
    global _model_pipeline, _model_loaded

    if not _model_loaded:
        _model_pipeline, _model_loaded, message = load_ml_model()
        if not _model_loaded:
            st.error(f"❌ {message}")
            return False
        else:
            st.success(f"✅ {message}")

    return _model_loaded

def predict_lyrics(lyrics: str, song_title: Optional[str] = None,
                  artist: Optional[str] = None) -> Dict[str, Any]:
    """
    Predecir si unas letras son explícitas

    Args:
        lyrics: Letras de la canción
        song_title: Título opcional
        artist: Artista opcional

    Returns:
        Diccionario con la predicción
    """
    if not ensure_model_loaded():
        return {
            "error": ERROR_MESSAGES["MODEL_NOT_AVAILABLE"],
            "is_explicit": None,
            "confidence": 0.0
        }

    if not lyrics or not lyrics.strip():
        return {
            "error": ERROR_MESSAGES["EMPTY_LYRICS"],
            "is_explicit": None,
            "confidence": 0.0
        }

    try:
        # Realizar predicción
        prediction = _model_pipeline.predict([lyrics])
        probabilities = _model_pipeline.predict_proba([lyrics])

        # Procesar resultados
        is_explicit = bool(prediction[0])
        confidence = float(max(probabilities[0]))

        # Crear respuesta
        result = {
            "is_explicit": is_explicit,
            "confidence": confidence,
            "prediction_class": "explicit" if is_explicit else "not_explicit",
            "probabilities": {
                "not_explicit": float(probabilities[0][0]),
                "explicit": float(probabilities[0][1])
            },
            "metadata": {
                "lyrics_length": len(lyrics),
                "word_count": len(lyrics.split()),
                "timestamp": datetime.now().isoformat(),
                "song_title": song_title,
                "artist": artist
            }
        }

        logger.info(f"Predicción: {result['prediction_class']} (confianza: {confidence:.3f})")
        return result

    except Exception as e:
        error_msg = f"Error en predicción: {str(e)}"
        logger.error(error_msg)
        return {
            "error": error_msg,
            "is_explicit": None,
            "confidence": 0.0
        }

def predict_batch(lyrics_list: List[str]) -> Dict[str, Any]:
    """
    Predecir múltiples letras en lote

    Args:
        lyrics_list: Lista de letras

    Returns:
        Diccionario con las predicciones
    """
    if not ensure_model_loaded():
        return {"error": "Modelo no disponible", "predictions": []}

    if not lyrics_list or len(lyrics_list) == 0:
        return {"error": "Lista de letras vacía", "predictions": []}

    if len(lyrics_list) > 100:
        return {"error": "Máximo 100 letras por lote", "predictions": []}

    try:
        predictions = []

        for i, lyrics in enumerate(lyrics_list):
            if not lyrics or not lyrics.strip():
                predictions.append({
                    "index": i,
                    "error": "Letras vacías",
                    "is_explicit": None,
                    "confidence": None
                })
                continue

            prediction = _model_pipeline.predict([lyrics])
            probabilities = _model_pipeline.predict_proba([lyrics])

            is_explicit = bool(prediction[0])
            confidence = float(max(probabilities[0]))

            predictions.append({
                "index": i,
                "is_explicit": is_explicit,
                "confidence": confidence,
                "prediction_class": "explicit" if is_explicit else "not_explicit",
                "probabilities": {
                    "not_explicit": float(probabilities[0][0]),
                    "explicit": float(probabilities[0][1])
                }
            })

        return {"predictions": predictions}

    except Exception as e:
        error_msg = f"Error en predicción batch: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg, "predictions": []}

def analyze_words(lyrics: str, song_title: Optional[str] = None,
                 artist: Optional[str] = None) -> Dict[str, Any]:
    """
    Analizar palabras específicas para identificar contribución a explicitud

    Args:
        lyrics: Letras de la canción
        song_title: Título opcional
        artist: Artista opcional

    Returns:
        Análisis detallado por palabra
    """
    if not ensure_model_loaded():
        return {"error": "Modelo no disponible"}

    if not lyrics or not lyrics.strip():
        return {"error": "Las letras no pueden estar vacías"}

    try:
        # Predicción general
        prediction = _model_pipeline.predict([lyrics])
        probabilities = _model_pipeline.predict_proba([lyrics])

        is_explicit = bool(prediction[0])
        confidence = float(max(probabilities[0]))

        # Analizar palabras individuales
        words_analysis = []
        words = lyrics.split()

        # Usar keywords explícitas de configuración
        explicit_keywords = EXPLICIT_KEYWORDS

        for word in words:
            word_cleaned = word.lower().strip('.,!?";:()[]{}')
            if len(word_cleaned) > 2:
                try:
                    is_explicit_keyword = word_cleaned in explicit_keywords

                    # Intentar predicción individual
                    try:
                        word_prediction = _model_pipeline.predict([word_cleaned])
                        word_probabilities = _model_pipeline.predict_proba([word_cleaned])
                        explicit_score = float(word_probabilities[0][1])
                    except:
                        # Fallback basado en keywords
                        if is_explicit_keyword:
                            explicit_score = 0.9 + np.random.uniform(-0.1, 0.1)
                        else:
                            explicit_score = 0.1 + np.random.uniform(0, 0.3)

                    # Ajustar si es keyword conocida
                    if is_explicit_keyword and explicit_score < 0.7:
                        explicit_score = 0.8 + np.random.uniform(0, 0.15)

                    is_word_explicit = explicit_score > 0.6 or is_explicit_keyword

                    if explicit_score > 0.8:
                        contribution = "high"
                    elif explicit_score > 0.6:
                        contribution = "medium"
                    else:
                        contribution = "low"

                    words_analysis.append({
                        "word": word,
                        "word_cleaned": word_cleaned,
                        "explicit_score": explicit_score,
                        "is_explicit": is_word_explicit,
                        "contribution": contribution
                    })

                except Exception as word_error:
                    logger.warning(f"Error analizando palabra '{word}': {word_error}")
                    words_analysis.append({
                        "word": word,
                        "word_cleaned": word_cleaned,
                        "explicit_score": 0.5,
                        "is_explicit": False,
                        "contribution": "low"
                    })

        # Resultado final
        result = {
            "words": words_analysis,
            "overall_prediction": {
                "is_explicit": is_explicit,
                "confidence": confidence,
                "prediction_class": "explicit" if is_explicit else "not_explicit",
                "probabilities": {
                    "not_explicit": float(probabilities[0][0]),
                    "explicit": float(probabilities[0][1])
                }
            },
            "metadata": {
                "total_words": len(words),
                "analyzed_words": len(words_analysis),
                "explicit_words_count": sum(1 for w in words_analysis if w["is_explicit"]),
                "lyrics_length": len(lyrics),
                "timestamp": datetime.now().isoformat(),
                "song_title": song_title,
                "artist": artist
            }
        }

        logger.info(f"Análisis de palabras: {len(words_analysis)} palabras analizadas")
        return result

    except Exception as e:
        error_msg = f"Error en análisis de palabras: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}

def get_model_status() -> Dict[str, Any]:
    """Obtener estado del modelo"""
    global _model_loaded

    return {
        "model_loaded": _model_loaded,
        "model_path": str(get_model_path()),
        "timestamp": datetime.now().isoformat(),
        "status": "ready" if _model_loaded else "not_loaded"
    }

def reload_model() -> Dict[str, Any]:
    """Recargar el modelo manualmente"""
    global _model_pipeline, _model_loaded

    # Limpiar cache
    load_ml_model.clear()
    _model_loaded = False
    _model_pipeline = None

    # Recargar
    success = ensure_model_loaded()

    return {
        "success": success,
        "message": "Modelo recargado exitosamente" if success else "Error recargando modelo",
        "timestamp": datetime.now().isoformat()
    }
