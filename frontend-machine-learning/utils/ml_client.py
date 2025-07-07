"""
Cliente ML integrado - Reemplaza las llamadas API con funciones locales
"""

import streamlit as st
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import de funciones ML locales
try:
    from .ml_functions import (
        predict_lyrics as ml_predict_lyrics,
        predict_batch as ml_predict_batch,
        analyze_words as ml_analyze_words,
        get_model_status,
        reload_model,
        ensure_model_loaded
    )
    ML_AVAILABLE = True
except ImportError as e:
    st.error(f"Error importando funciones ML: {e}")
    ML_AVAILABLE = False

class MLClient:
    """Cliente ML integrado que reemplaza las llamadas a API externa"""

    def __init__(self):
        self.ml_available = ML_AVAILABLE

    def check_health(self) -> Dict[str, Any]:
        """Verificar el estado del sistema ML"""
        if not self.ml_available:
            return {
                "status": "error",
                "message": "Funciones ML no disponibles",
                "model_loaded": False,
                "timestamp": datetime.now().isoformat()
            }

        try:
            status = get_model_status()
            return {
                "status": "healthy" if status["model_loaded"] else "unhealthy",
                "model_loaded": status["model_loaded"],
                "timestamp": status["timestamp"],
                "message": "Sistema ML funcionando correctamente" if status["model_loaded"] else "Modelo no cargado"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error verificando estado: {str(e)}",
                "model_loaded": False,
                "timestamp": datetime.now().isoformat()
            }

    def predict_lyrics(self, lyrics: str, song_title: Optional[str] = None,
                      artist: Optional[str] = None) -> Dict[str, Any]:
        """
        Predecir si las letras son explícitas usando ML local

        Args:
            lyrics: Letras de la canción
            song_title: Título de la canción (opcional)
            artist: Artista (opcional)

        Returns:
            Diccionario con la predicción
        """
        if not self.ml_available:
            return {"error": "Sistema ML no disponible"}

        try:
            return ml_predict_lyrics(lyrics, song_title, artist)
        except Exception as e:
            error_msg = f"Error en predicción ML: {str(e)}"
            st.error(error_msg)
            return {"error": error_msg}

    def analyze_words(self, lyrics: str, song_title: Optional[str] = None,
                     artist: Optional[str] = None) -> Dict[str, Any]:
        """
        Analizar palabras específicas de las letras usando ML local

        Args:
            lyrics: Letras de la canción
            song_title: Título de la canción (opcional)
            artist: Artista (opcional)

        Returns:
            Diccionario con el análisis por palabra
        """
        if not self.ml_available:
            return {"error": "Sistema ML no disponible"}

        try:
            return ml_analyze_words(lyrics, song_title, artist)
        except Exception as e:
            error_msg = f"Error en análisis de palabras: {str(e)}"
            st.error(error_msg)
            return {"error": error_msg}

    def predict_batch(self, lyrics_list: List[str]) -> Dict[str, Any]:
        """
        Predecir múltiples letras en lote usando ML local

        Args:
            lyrics_list: Lista de letras

        Returns:
            Diccionario con las predicciones
        """
        if not self.ml_available:
            return {"error": "Sistema ML no disponible", "predictions": []}

        try:
            return ml_predict_batch(lyrics_list)
        except Exception as e:
            error_msg = f"Error en predicción batch: {str(e)}"
            st.error(error_msg)
            return {"error": error_msg, "predictions": []}

    def reload_model(self) -> Dict[str, Any]:
        """Recargar el modelo ML"""
        if not self.ml_available:
            return {"success": False, "message": "Sistema ML no disponible"}

        try:
            return reload_model()
        except Exception as e:
            error_msg = f"Error recargando modelo: {str(e)}"
            return {"success": False, "message": error_msg}

# Función para migración gradual - detecta si usar API o ML local
def get_smart_client():
    """
    Obtiene un cliente inteligente que usa ML local si está disponible,
    sino intenta usar la API externa como fallback
    """
    # Intentar usar ML local primero
    ml_client = MLClient()
    if ml_client.ml_available:
        health = ml_client.check_health()
        if health["status"] in ["healthy", "unhealthy"]:  # ML disponible aunque modelo no esté cargado
            st.info("🔧 Usando sistema ML integrado (sin API externa)")
            return ml_client

    # Fallback a API externa si ML local no está disponible
    st.warning("⚠️ ML local no disponible, intentando API externa...")
    try:
        from .api_client import APIClient
        api_client = APIClient()
        health = api_client.check_health()
        if health["status"] != "error":
            st.info("🌐 Usando API externa")
            return api_client
    except Exception as e:
        st.error(f"API externa tampoco disponible: {e}")

    # Si nada funciona, retornar ML client para mostrar errores apropiados
    return ml_client

# Instancia global del cliente inteligente
smart_client = None

def get_client():
    """Obtener cliente global, creándolo si es necesario"""
    global smart_client
    if smart_client is None:
        smart_client = get_smart_client()
    return smart_client

# Funciones de conveniencia que mantienen la API original
def check_api_status() -> bool:
    """Verificar si el sistema ML/API está disponible"""
    try:
        client = get_client()
        health = client.check_health()
        return health.get("status") == "healthy"
    except:
        return False

def predict_lyrics_safe(lyrics: str, song_title: Optional[str] = None,
                       artist: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Versión segura de predicción que maneja errores

    Returns:
        Predicción o None si hay error
    """
    try:
        client = get_client()
        result = client.predict_lyrics(lyrics, song_title, artist)
        if "error" not in result:
            return result
        return None
    except:
        return None

def analyze_words_safe(lyrics: str, song_title: Optional[str] = None,
                      artist: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Versión segura de análisis de palabras que maneja errores

    Returns:
        Análisis o None si hay error
    """
    try:
        client = get_client()
        result = client.analyze_words(lyrics, song_title, artist)
        if "error" not in result:
            return result
        return None
    except:
        return None

def format_confidence(confidence: float) -> tuple[str, str]:
    """
    Formatear la confianza del modelo

    Args:
        confidence: Valor de confianza (0-1)

    Returns:
        Tupla con (texto_formateado, clase_css)
    """
    percentage = confidence * 100

    if confidence >= 0.8:
        return f"{percentage:.1f}%", "confidence-high"
    elif confidence >= 0.6:
        return f"{percentage:.1f}%", "confidence-medium"
    else:
        return f"{percentage:.1f}%", "confidence-low"

def get_confidence_description(confidence: float) -> str:
    """
    Obtener descripción textual de la confianza

    Args:
        confidence: Valor de confianza (0-1)

    Returns:
        Descripción textual
    """
    if confidence >= 0.9:
        return "Muy seguro"
    elif confidence >= 0.8:
        return "Bastante seguro"
    elif confidence >= 0.7:
        return "Moderadamente seguro"
    elif confidence >= 0.6:
        return "Poco seguro"
    else:
        return "Muy incierto"
