"""
Administrador de datos para cargar y manejar el dataset de canciones
Actualizado para usar las nuevas columnas del dataset
"""

import pandas as pd
import streamlit as st
from typing import Dict, Any, List, Optional, Tuple
import os
from pathlib import Path

# Imports para funciones de cache seguras
from .cache_helpers import cached_load_dataset, display_dataset_status, get_dataset_stats
from .config import DATA_PATH

# Constante para el nombre del dataset
DATASET_FILENAME = "spotify_dataset_sin_duplicados_4.csv"

# Ruta al dataset usando configuración automática
DATASET_PATH = str(DATA_PATH)

# Verificar si el dataset existe y mostrar información de debug
if not Path(DATASET_PATH).exists():
    print(f"❌ Dataset no encontrado en: {DATASET_PATH}")
    print(f"📁 Directorio actual: {os.getcwd()}")
    print(f"📁 Directorio del archivo: {Path(__file__).parent}")
    print(f"📁 Base path configurado: {DATA_PATH.parent}")

    # Buscar el dataset en ubicaciones alternativas
    alternative_paths = [
        Path.cwd() / "data" / DATASET_FILENAME,
        Path.cwd() / "frontend-machine-learning" / "data" / DATASET_FILENAME,
        Path(__file__).parent.parent / "data" / DATASET_FILENAME,
    ]

    for alt_path in alternative_paths:
        if alt_path.exists():
            print(f"✅ Dataset encontrado en ubicación alternativa: {alt_path}")
            DATASET_PATH = str(alt_path)
            break
    else:
        print("💀 No se pudo encontrar el dataset en ninguna ubicación")
else:
    print(f"✅ Dataset encontrado en: {DATASET_PATH}")

# Mapeo de columnas del nuevo dataset (después del renombrado en cache_helpers)
COLUMN_MAPPING = {
    'title': 'title',           # Ya renombrado de 'song'
    'artist': 'artist',         # Ya renombrado de 'Artist(s)'
    'lyrics': 'lyrics',         # Ya renombrado de 'text'
    'explicit': 'explicit',     # Ya renombrado de 'Explicit'
    'genre': 'genre',           # Ya renombrado de 'Genre'
    'album': 'Album',
    'release_date': 'Release Date',
    'popularity': 'Popularity',
    'energy': 'Energy',
    'danceability': 'Danceability',
    'tempo': 'Tempo'
}

class DataManager:
    """Clase para manejar el dataset de canciones con nuevas columnas"""

    def __init__(self, dataset_path: str = DATASET_PATH):
        self.dataset_path = dataset_path
        self._df = None
        self._loaded = False

    def load_dataset(self) -> pd.DataFrame:
        """
        Cargar el dataset con manejo de errores

        Returns:
            DataFrame con el dataset
        """
        # Usar función de cache segura
        df, message, success = cached_load_dataset(self.dataset_path)

        if success and not df.empty:
            self._df = df
            self._loaded = True
            display_dataset_status(df, message, success)
            return df
        else:
            st.error(f"❌ {message}")
            return pd.DataFrame()

    def get_dataset(self) -> pd.DataFrame:
        """
        Obtener el dataset cargado

        Returns:
            DataFrame con el dataset
        """
        if not self._loaded or self._df is None:
            return self.load_dataset()
        return self._df

    def search_songs(self, title_query: str = "", artist_query: str = "",
                    page: int = 1, per_page: int = 10) -> Tuple[List[Dict], int]:
        """
        Buscar canciones por título y/o artista con paginación

        Args:
            title_query: Consulta para el título
            artist_query: Consulta para el artista
            page: Número de página (1-indexed)
            per_page: Canciones por página

        Returns:
            Tupla con (lista de canciones, total de resultados)
        """
        df = self.get_dataset()

        if df.empty:
            return [], 0

        # Aplicar filtros
        mask = pd.Series([True] * len(df))

        if title_query.strip():
            mask &= df[COLUMN_MAPPING['title']].str.contains(
                title_query, case=False, na=False
            )

        if artist_query.strip():
            mask &= df[COLUMN_MAPPING['artist']].str.contains(
                artist_query, case=False, na=False
            )

        # Aplicar filtro
        df_filtered = df[mask]
        total_results = len(df_filtered)

        # Paginación
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        df_page = df_filtered.iloc[start_idx:end_idx]

        # Convertir a lista de diccionarios
        songs = []
        for _, row in df_page.iterrows():
            songs.append(self._row_to_dict(row))

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

        # Buscar coincidencias exactas (case insensitive)
        mask = (
            df[COLUMN_MAPPING['title']].str.lower() == title.lower()
        ) & (
            df[COLUMN_MAPPING['artist']].str.lower() == artist.lower()
        )

        matches = df[mask]

        if matches.empty:
            return None

        # Retornar la primera coincidencia
        row = matches.iloc[0]
        return self._row_to_dict(row)
    
    def get_id(self, title: str, artist: str) -> Optional[Dict]:
        df = self.get_dataset()

        if df.empty:
            return None

        # Buscar coincidencias exactas (case insensitive)
        mask = (
            df[COLUMN_MAPPING['title']].str.lower() == title.lower()
        ) & (
            df[COLUMN_MAPPING['artist']].str.lower() == artist.lower()
        )

        matches = df[mask]

        if matches.empty:
            return None

        # Retornar la primera coincidencia
        # row = matches.iloc[0]
        return matches.index[0] 


    def get_suggestions(self, title: str, artist: str) -> List[Dict]:
        """
        Obtener sugerencias basadas en las columnas Similar de Spotify

        Args:
            title: Título de la canción
            artist: Artista

        Returns:
            Lista de canciones sugeridas
        """
        # Buscar la canción original
        original_song = self.get_song_by_title_artist(title, artist)

        if not original_song:
            return []

        df = self.get_dataset()
        suggestions = []

        # Buscar canciones similares en el dataset si existen columnas de similitud
        similarity_cols = [
            ('Similar Artist 1', 'Similar Song 1'),
            ('Similar Artist 2', 'Similar Song 2'),
            ('Similar Artist 3', 'Similar Song 3')
        ]

        for artist_col, song_col in similarity_cols:
            if artist_col in df.columns and song_col in df.columns:
                # Buscar por el artista y canción originales
                mask = (
                    df[COLUMN_MAPPING['title']].str.lower() == title.lower()
                ) & (
                    df[COLUMN_MAPPING['artist']].str.lower() == artist.lower()
                )

                matches = df[mask]

                for _, row in matches.iterrows():
                    similar_artist = row.get(artist_col, '')
                    similar_song = row.get(song_col, '')

                    if similar_artist and similar_song:
                        # Buscar la canción similar en el dataset
                        similar_match = self.get_song_by_title_artist(similar_song, similar_artist)
                        if similar_match:
                            suggestions.append(similar_match)

        # Si no hay suficientes sugerencias, buscar por género
        if len(suggestions) < 3:
            genre = original_song.get('genre', '')
            if genre and genre != 'Desconocido':
                genre_songs = self.search_songs_by_genre(genre, page=1, per_page=5)[0]
                for song in genre_songs:
                    if (song['title'].lower() != title.lower() or
                        song['artist'].lower() != artist.lower()):
                        suggestions.append(song)
                        if len(suggestions) >= 5:
                            break

        return suggestions[:5]  # Máximo 5 sugerencias

    def search_songs_by_genre(self, genre_query: str, page: int = 1, per_page: int = 10) -> Tuple[List[Dict], int]:
        """
        Buscar canciones por género

        Args:
            genre_query: Consulta para el género
            page: Número de página
            per_page: Canciones por página

        Returns:
            Tupla con (lista de canciones, total de resultados)
        """
        df = self.get_dataset()

        if df.empty:
            return [], 0

        # Filtrar por género
        mask = df[COLUMN_MAPPING['genre']].str.contains(
            genre_query, case=False, na=False
        )

        df_filtered = df[mask]
        total_results = len(df_filtered)

        # Paginación
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        df_page = df_filtered.iloc[start_idx:end_idx]

        # Convertir a lista de diccionarios
        songs = []
        for _, row in df_page.iterrows():
            songs.append(self._row_to_dict(row))

        return songs, total_results

    def _row_to_dict(self, row) -> Dict:
        """
        Convertir una fila del DataFrame a diccionario

        Args:
            row: Fila del DataFrame

        Returns:
            Diccionario con la información de la canción
        """
        return {
            'title': row.get(COLUMN_MAPPING['title'], ''),
            'artist': row.get(COLUMN_MAPPING['artist'], ''),
            'genre': row.get(COLUMN_MAPPING['genre'], 'Desconocido'),
            'lyrics': row.get(COLUMN_MAPPING['lyrics'], ''),
            'is_explicit': bool(row.get('is_explicit', False)),  # Usar el campo creado en cache_helpers
            'explicit_label': 'Explícito' if row.get('is_explicit', False) else 'Limpio',
            'album': row.get(COLUMN_MAPPING.get('album', 'album'), ''),
            'release_date': row.get(COLUMN_MAPPING.get('release_date', 'release_date'), ''),
            'popularity': row.get(COLUMN_MAPPING.get('popularity', 'popularity'), 0),
            'energy': row.get(COLUMN_MAPPING.get('energy', 'energy'), 0),
            'danceability': row.get(COLUMN_MAPPING.get('danceability', 'danceability'), 0),
            'tempo': row.get(COLUMN_MAPPING.get('tempo', 'tempo'), 0)
        }

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del dataset

        Returns:
            Diccionario con estadísticas
        """
        df = self.get_dataset()

        if df.empty:
            return {}

        stats = get_dataset_stats(df)

        # Agregar estadísticas específicas del nuevo dataset
        if 'is_explicit' in df.columns:
            explicit_count = df['is_explicit'].sum()
            stats['explicit_songs'] = int(explicit_count)
            stats['clean_songs'] = len(df) - int(explicit_count)
            stats['explicit_percentage'] = (explicit_count / len(df)) * 100

        if COLUMN_MAPPING['genre'] in df.columns:
            stats['unique_genres'] = df[COLUMN_MAPPING['genre']].nunique()
            stats['top_genres'] = df[COLUMN_MAPPING['genre']].value_counts().head(5).to_dict()

        return stats

# Instancia global del administrador de datos
data_manager = DataManager()

# Funciones de conveniencia para mantener compatibilidad
def search_songs_paginated(title_query: str = "", artist_query: str = "",
                         page: int = 1, per_page: int = 10) -> Tuple[List[Dict], int, int]:
    """
    Buscar canciones con paginación - función de conveniencia

    Returns:
        Tupla con (canciones, total, total_pages)
    """
    songs, total = data_manager.search_songs(title_query, artist_query, page, per_page)
    total_pages = (total + per_page - 1) // per_page
    return songs, total, total_pages

def search_songs_by_genre_paginated(genre_query: str = "", page: int = 1, per_page: int = 10) -> Tuple[List[Dict], int, int]:
    """
    Buscar canciones por género con paginación - función de conveniencia

    Returns:
        Tupla con (canciones, total, total_pages)
    """
    songs, total = data_manager.search_songs_by_genre(genre_query, page, per_page)
    total_pages = (total + per_page - 1) // per_page
    return songs, total, total_pages

def get_song_by_title_artist(title: str, artist: str) -> Optional[Dict]:
    """Función de conveniencia para obtener una canción específica"""
    return data_manager.get_song_by_title_artist(title, artist)
def get_id_chi(title: str, artist: str) -> Optional[Dict]:
    return data_manager.get_id(title,  artist)


def get_suggestions(title: str, artist: str) -> List[Dict]:
    """Función de conveniencia para obtener sugerencias"""
    return data_manager.get_suggestions(title, artist)
