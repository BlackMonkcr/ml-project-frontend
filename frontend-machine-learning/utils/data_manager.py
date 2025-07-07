"""
Administrador de datos para cargar y manejar el dataset de canciones
"""

import pandas as pd
import streamlit as st
from typing import Dict, Any, List, Optional, Tuple
import os
from pathlib import Path

# Ruta al dataset
DATASET_PATH = "data/spotify_dataset_sin_duplicados_4.csv"

class DataManager:
    """Clase para manejar el dataset de canciones"""
    
    def __init__(self, dataset_path: str = DATASET_PATH):
        self.dataset_path = dataset_path
        self._df = None
        self._loaded = False
    
    @st.cache_data
    def load_dataset(_self) -> pd.DataFrame:
        """
        Cargar el dataset con cache de Streamlit
        
        Returns:
            DataFrame con el dataset
        """
        try:
            if not os.path.exists(_self.dataset_path):
                st.error(f"Dataset no encontrado en: {_self.dataset_path}")
                return pd.DataFrame()
            
            # Cargar solo las columnas necesarias para optimizar memoria
            columns_to_load = [
                'Artist(s)', 'song', 'text', 'Genre', 'Explicit',
                'Similar Artist 1', 'Similar Song 1', 'Similarity Score 1',
                'Similar Artist 2', 'Similar Song 2', 'Similarity Score 2',
                'Similar Artist 3', 'Similar Song 3', 'Similarity Score 3'
            ]
            
            df = pd.read_csv(_self.dataset_path, usecols=columns_to_load)
            
            # Limpiar datos
            df = df.dropna(subset=['song', 'Artist(s)', 'text'])
            df = df.reset_index(drop=True)
            
            # Normalizar nombres de columnas
            df = df.rename(columns={
                'Artist(s)': 'artist',
                'song': 'title',
                'text': 'lyrics',
                'Genre': 'genre',
                'Explicit': 'explicit'
            })
            
            # Convertir explicit a booleano
            df['is_explicit'] = df['explicit'].str.lower() == 'yes'
            
            _self._df = df
            _self._loaded = True
            
            return df
            
        except Exception as e:
            st.error(f"Error cargando dataset: {e}")
            return pd.DataFrame()
    
    @property
    def df(self) -> pd.DataFrame:
        """Propiedad para acceso directo al DataFrame"""
        return self.get_dataset()
    
    def get_dataset(self) -> pd.DataFrame:
        """Obtener el dataset cargado"""
        if not self._loaded:
            return self.load_dataset()
        return self._df if self._df is not None else pd.DataFrame()
    
    def search_songs(self, title_query: str = "", artist_query: str = "",
                    page: int = 1, per_page: int = 10) -> Tuple[List[Dict], int]:
        """
        Buscar canciones por título y/o artista
        
        Args:
            title_query: Consulta para el título
            artist_query: Consulta para el artista
            page: Número de página (1-indexed)
            per_page: Resultados por página
            
        Returns:
            Tupla con (lista_de_canciones, total_resultados)
        """
        df = self.get_dataset()
        
        if df.empty:
            return [], 0
        
        # Filtrar por título si se proporciona
        if title_query.strip():
            mask_title = df['title'].str.contains(
                title_query.strip(), 
                case=False, 
                na=False, 
                regex=False
            )
            df = df[mask_title]
        
        # Filtrar por artista si se proporciona
        if artist_query.strip():
            mask_artist = df['artist'].str.contains(
                artist_query.strip(), 
                case=False, 
                na=False, 
                regex=False
            )
            df = df[mask_artist]
        
        total_results = len(df)
        
        # Paginación
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        df_page = df.iloc[start_idx:end_idx]
        
        # Convertir a lista de diccionarios
        songs = []
        for _, row in df_page.iterrows():
            songs.append({
                'title': row['title'],
                'artist': row['artist'],
                'genre': row.get('genre', 'Desconocido'),
                'lyrics': row['lyrics'],
                'is_explicit': row['is_explicit'],
                'explicit_label': row['explicit']
            })
        
        return songs, total_results
    
    def get_song_by_title_artist(self, title: str, artist: str) -> Optional[Dict]:
        """
        Obtener una canción específica por título y artista
        
        Args:
            title: Título de la canción
            artist: Artista
            
        Returns:
            Diccionario con la información de la canción o None
        """
        df = self.get_dataset()
        
        if df.empty:
            return None
        
        # Buscar coincidencia exacta (ignorando mayúsculas)
        mask = (df['title'].str.lower() == title.lower()) & \
               (df['artist'].str.lower() == artist.lower())
        
        matches = df[mask]
        
        if matches.empty:
            return None
        
        # Retornar la primera coincidencia
        row = matches.iloc[0]
        return {
            'title': row['title'],
            'artist': row['artist'],
            'genre': row.get('genre', 'Desconocido'),
            'lyrics': row['lyrics'],
            'is_explicit': row['is_explicit'],
            'explicit_label': row['explicit']
        }
    
    def get_suggestions(self, title: str, artist: str) -> List[Dict]:
        """
        Obtener sugerencias basadas en las columnas Similar de Spotify
        
        Args:
            title: Título de la canción
            artist: Artista
            
        Returns:
            Lista de canciones sugeridas
        """
        df = self.get_dataset()
        
        if df.empty:
            return []
        
        # Buscar la canción original
        mask = (df['title'].str.lower() == title.lower()) & \
               (df['artist'].str.lower() == artist.lower())
        
        matches = df[mask]
        
        if matches.empty:
            return []
        
        row = matches.iloc[0]
        suggestions = []
        
        # Obtener las 3 sugerencias de Spotify
        for i in range(1, 4):
            similar_artist = row.get(f'Similar Artist {i}')
            similar_song = row.get(f'Similar Song {i}')
            similarity_score = row.get(f'Similarity Score {i}')
            
            if pd.notna(similar_artist) and pd.notna(similar_song):
                # Buscar la canción sugerida en el dataset
                suggested_song = self.get_song_by_title_artist(similar_song, similar_artist)
                
                if suggested_song:
                    suggested_song['similarity_score'] = similarity_score
                    suggestions.append(suggested_song)
        
        return suggestions
    
    def search_songs_by_genre(self, genre_query: str, page: int = 1, per_page: int = 10) -> Tuple[List[Dict], int]:
        """
        Buscar canciones por género
        
        Args:
            genre_query: Consulta para el género
            page: Número de página (1-indexed)
            per_page: Resultados por página
            
        Returns:
            Tupla con (lista_de_canciones, total_resultados)
        """
        df = self.get_dataset()
        
        if df.empty:
            return [], 0
        
        # Filtrar por género
        if genre_query.strip():
            mask_genre = df['genre'].str.contains(
                genre_query.strip(), 
                case=False, 
                na=False, 
                regex=False
            )
            df = df[mask_genre]
        
        total_results = len(df)
        
        # Paginación
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        df_page = df.iloc[start_idx:end_idx]
        
        # Convertir a lista de diccionarios
        songs = []
        for _, row in df_page.iterrows():
            songs.append({
                'title': row['title'],
                'artist': row['artist'],
                'genre': row.get('genre', 'Desconocido'),
                'lyrics': row['lyrics'],
                'is_explicit': row['is_explicit'],
                'explicit_label': row['explicit']
            })
        
        return songs, total_results

# Instancia global del administrador de datos
data_manager = DataManager()

@st.cache_data
def load_dataset_info() -> Dict[str, Any]:
    """Cargar información básica del dataset"""
    df = data_manager.get_dataset()
    
    if df.empty:
        return {
            'total_songs': 0,
            'explicit_count': 0,
            'explicit_percentage': 0.0
        }
    
    total = len(df)
    explicit_count = df['is_explicit'].sum()
    explicit_percentage = (explicit_count / total) * 100 if total > 0 else 0
    
    return {
        'total_songs': total,
        'explicit_count': int(explicit_count),
        'explicit_percentage': explicit_percentage
    }

@st.cache_data
def get_quick_stats() -> Dict[str, Any]:
    """Obtener estadísticas rápidas del dataset"""
    info = load_dataset_info()
    
    return {
        'total': info['total_songs'],
        'explicit': info['explicit_count'],
        'explicit_percentage': info['explicit_percentage']
    }

def search_songs_paginated(title_query: str = "", artist_query: str = "",
                          page: int = 1, per_page: int = 10) -> Tuple[List[Dict], int, int]:
    """
    Buscar canciones con paginación
    
    Returns:
        Tupla con (lista_de_canciones, total_resultados, total_páginas)
    """
    songs, total = data_manager.search_songs(title_query, artist_query, page, per_page)
    total_pages = (total + per_page - 1) // per_page  # Ceiling division
    
    return songs, total, total_pages

def search_songs_by_genre_paginated(genre_query: str = "", page: int = 1, per_page: int = 10) -> Tuple[List[Dict], int, int]:
    """
    Buscar canciones por género con paginación
    
    Args:
        genre_query: Consulta para el género
        page: Número de página (1-indexed)
        per_page: Resultados por página
    
    Returns:
        Tupla con (lista_de_canciones, total_resultados, total_páginas)
    """
    songs, total = data_manager.search_songs_by_genre(genre_query, page, per_page)
    total_pages = (total + per_page - 1) // per_page  # Ceiling division
    
    return songs, total, total_pages

def get_dataset_sample(n=10) -> List[Dict]:
    """
    Obtener una muestra del dataset para debugging
    
    Args:
        n: Número de canciones a mostrar
        
    Returns:
        Lista de canciones de ejemplo
    """
    df = data_manager.get_dataset()
    
    if df.empty:
        return []
    
    # Tomar una muestra aleatoria
    sample_df = df.head(n)  # Usar head en lugar de sample para debugging
    
    songs = []
    for _, row in sample_df.iterrows():
        songs.append({
            'title': row['title'],
            'artist': row['artist'],
            'genre': row.get('genre', 'Desconocido'),
            'is_explicit': row['is_explicit'],
            'explicit_label': row['explicit']
        })
    
    return songs

def debug_dataset_info() -> Dict[str, Any]:
    """Información de debug del dataset"""
    df = data_manager.get_dataset()
    
    if df.empty:
        return {"error": "Dataset vacío"}
    
    return {
        "total_rows": len(df),
        "columns": list(df.columns),
        "sample_titles": df['title'].head(10).tolist(),
        "sample_artists": df['artist'].head(10).tolist(),
        "explicit_distribution": df['is_explicit'].value_counts().to_dict()
    }
