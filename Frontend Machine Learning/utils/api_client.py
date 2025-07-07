"""
Cliente para conectar con la API FastAPI del modelo de ML
"""

import requests
import streamlit as st
from typing import Dict, Any, Optional, List
import json

# Configuración de la API
API_BASE_URL = "http://localhost:8000"

class APIClient:
    """Cliente para interactuar con la API FastAPI"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        
    def check_health(self) -> Dict[str, Any]:
        """Verificar el estado de la API"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error conectando con la API: {e}")
            return {"status": "error", "message": str(e)}
    
    def predict_lyrics(self, lyrics: str, song_title: Optional[str] = None, 
                      artist: Optional[str] = None) -> Dict[str, Any]:
        """
        Predecir si las letras son explícitas
        
        Args:
            lyrics: Letras de la canción
            song_title: Título de la canción (opcional)
            artist: Artista (opcional)
            
        Returns:
            Diccionario con la predicción
        """
        try:
            payload = {
                "lyrics": lyrics,
                "song_title": song_title,
                "artist": artist
            }
            
            response = self.session.post(
                f"{self.base_url}/predict",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            st.error(f"Error en predicción: {e}")
            return {"error": str(e)}
    
    def analyze_words(self, lyrics: str, song_title: Optional[str] = None,
                     artist: Optional[str] = None) -> Dict[str, Any]:
        """
        Analizar palabras específicas de las letras
        
        Args:
            lyrics: Letras de la canción
            song_title: Título de la canción (opcional)
            artist: Artista (opcional)
            
        Returns:
            Diccionario con el análisis por palabra
        """
        try:
            payload = {
                "lyrics": lyrics,
                "song_title": song_title,
                "artist": artist
            }
            
            response = self.session.post(
                f"{self.base_url}/analyze-words",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            st.error(f"Error en análisis de palabras: {e}")
            return {"error": str(e)}
    
    def predict_batch(self, lyrics_list: List[str]) -> Dict[str, Any]:
        """
        Predecir múltiples letras en lote
        
        Args:
            lyrics_list: Lista de letras
            
        Returns:
            Diccionario con las predicciones
        """
        try:
            response = self.session.post(
                f"{self.base_url}/predict/batch",
                json=lyrics_list,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            st.error(f"Error en predicción por lotes: {e}")
            return {"error": str(e)}

# Instancia global del cliente
api_client = APIClient()

def check_api_status() -> bool:
    """Verificar si la API está disponible"""
    try:
        health = api_client.check_health()
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
        result = api_client.predict_lyrics(lyrics, song_title, artist)
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
        result = api_client.analyze_words(lyrics, song_title, artist)
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
