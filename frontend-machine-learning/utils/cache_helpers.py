"""
Utilidades para manejo de cache y widgets sin conflictos
"""

import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any

def safe_cache_load_dataset(dataset_path: str, columns_to_load: list) -> tuple[pd.DataFrame, str, bool]:
    """
    Función de carga de dataset sin widgets para cache seguro

    Returns:
        Tupla con (DataFrame, mensaje, success_flag)
    """
    try:
        if not pd.io.common.file_exists(dataset_path):
            return pd.DataFrame(), f"Dataset no encontrado: {dataset_path}", False

        df = pd.read_csv(dataset_path, usecols=columns_to_load)

        # Limpiar datos
        df = df.dropna(subset=['song', 'Artist(s)', 'text'])
        df = df.reset_index(drop=True)

        # Normalizar nombres
        df = df.rename(columns={
            'Artist(s)': 'artist',
            'song': 'title',
            'text': 'lyrics',
            'Genre': 'genre',
            'Explicit': 'explicit'
        })

        # Convertir explicit a booleano
        df['is_explicit'] = df['explicit'].str.lower() == 'yes'

        return df, f"Dataset cargado exitosamente: {len(df)} canciones", True

    except Exception as e:
        return pd.DataFrame(), f"Error cargando dataset: {str(e)}", False

@st.cache_data
def cached_load_dataset(dataset_path: str) -> tuple[pd.DataFrame, str, bool]:
    """Versión cacheada de la función de carga"""
    columns_to_load = [
        'Artist(s)', 'song', 'text', 'Genre', 'Explicit',
        'Similar Artist 1', 'Similar Song 1', 'Similarity Score 1',
        'Similar Artist 2', 'Similar Song 2', 'Similarity Score 2',
        'Similar Artist 3', 'Similar Song 3', 'Similarity Score 3'
    ]
    return safe_cache_load_dataset(dataset_path, columns_to_load)

def display_dataset_status(df: pd.DataFrame, message: str, success: bool):
    """Mostrar estado del dataset con widgets apropiados"""
    if success and not df.empty:
        st.success(f"✅ {message}")
    elif not success:
        st.error(f"❌ {message}")
    else:
        st.warning("⚠️ Dataset vacío después de la carga")

@st.cache_data
def get_dataset_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Obtener estadísticas del dataset de forma segura para cache"""
    if df.empty:
        return {
            'total_songs': 0,
            'explicit_count': 0,
            'explicit_percentage': 0.0,
            'genres': [],
            'artists': 0
        }

    total = len(df)
    explicit_count = df['is_explicit'].sum() if 'is_explicit' in df.columns else 0
    explicit_percentage = (explicit_count / total) * 100 if total > 0 else 0

    return {
        'total_songs': total,
        'explicit_count': int(explicit_count),
        'explicit_percentage': round(explicit_percentage, 2),
        'genres': df['genre'].unique().tolist() if 'genre' in df.columns else [],
        'artists': df['artist'].nunique() if 'artist' in df.columns else 0
    }
