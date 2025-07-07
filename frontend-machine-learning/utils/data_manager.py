"""
Administrador de datos para cargar y manejar el dataset de canciones
Incluye funcionalidades para manejar archivos grandes y descarga automática
"""

import pandas as pd
import streamlit as st
from typing import Dict, Any, List, Optional, Tuple
import os
from pathlib import Path
import requests
import hashlib
import zipfile

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
        Incluye manejo de archivos grandes

        Returns:
            DataFrame con el dataset
        """
        try:
            if not os.path.exists(_self.dataset_path):
                st.warning(f"Dataset no encontrado en: {_self.dataset_path}")
                # Intentar manejar dataset grande
                df = handle_large_dataset()
                if df is not None:
                    _self._df = df
                    _self._loaded = True
                    return df
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

# URLs de respaldo para el dataset
DATA_SOURCES = {
    "google_drive": "https://drive.google.com/file/d/1JGvJt-PZun28IfKGaeOAdjefmq9YPnxr/view?usp=sharing",
}

def download_from_url(url: str, output_path: Path) -> bool:
    """Descargar archivo desde URL directa con barra de progreso"""
    try:
        with st.spinner(f"Descargando dataset..."):
            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            progress_bar = st.progress(0)
            status_text = st.empty()

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if total_size > 0:
                            progress = downloaded / total_size
                            progress_bar.progress(progress)
                            status_text.text(f"Descargado: {downloaded / (1024*1024):.1f} MB de {total_size / (1024*1024):.1f} MB")

            progress_bar.empty()
            status_text.empty()
            return True
    except Exception as e:
        st.error(f"Error descargando: {e}")
        return False

def handle_large_dataset() -> Optional[pd.DataFrame]:
    """
    Manejar datasets grandes que no están en el repositorio
    """
    dataset_path = Path(DATASET_PATH)

    if dataset_path.exists():
        try:
            df = pd.read_csv(dataset_path)
            return df
        except Exception as e:
            st.warning(f"Error cargando dataset existente: {e}")

    st.warning("⚠️ Dataset no encontrado. Opciones disponibles:")

    # Opción 1: Upload manual
    with st.expander("📤 Opción 1: Subir archivo manualmente", expanded=True):
        st.markdown("""
        **El archivo CSV es muy grande para GitHub (211MB > 100MB límite)**

        Para usar la aplicación, sube tu archivo `spotify_dataset_sin_duplicados_4.csv`:
        """)

        uploaded_file = st.file_uploader(
            "Arrastra y suelta tu archivo CSV:",
            type=['csv'],
            help="Archivo spotify_dataset_sin_duplicados_4.csv (211MB)"
        )

        if uploaded_file is not None:
            try:
                # Crear directorio si no existe
                dataset_path.parent.mkdir(exist_ok=True)

                # Guardar archivo
                with open(dataset_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())

                # Verificar
                df = pd.read_csv(dataset_path)
                st.success(f"✅ Dataset cargado: {len(df)} canciones")
                st.rerun()

            except Exception as e:
                st.error(f"Error: {e}")

    # Opción 2: Descarga desde servicios en la nube
    with st.expander("☁️ Opción 2: Descargar desde la nube"):
        st.markdown("""
        **Configura una URL de descarga:**
        1. Sube tu CSV a Google Drive/Dropbox/GitHub Releases
        2. Obtén la URL de descarga directa
        3. Pégala aquí para descarga automática
        """)

        download_url = st.text_input("URL de descarga directa:")

        if download_url and st.button("📥 Descargar Dataset"):
            dataset_path.parent.mkdir(exist_ok=True)
            if download_from_url(download_url, dataset_path):
                try:
                    df = pd.read_csv(dataset_path)
                    st.success(f"✅ Descargado: {len(df)} canciones")
                    st.rerun()
                except Exception as e:
                    st.error(f"Archivo descargado pero corrupto: {e}")

    # Opción 3: Dataset de demo
    with st.expander("🔬 Opción 3: Usar datos de demo"):
        st.warning("Solo para pruebas - funcionalidad limitada")

        if st.button("📊 Crear Dataset Demo"):
            try:
                # Dataset mínimo para pruebas
                demo_data = {
                    'Artist(s)': ['Artist A', 'Artist B', 'Artist C'] * 10,
                    'song': [f'Song {i}' for i in range(30)],
                    'text': ['Sample lyrics for testing'] * 30,
                    'Genre': ['Pop', 'Rock', 'Hip-Hop'] * 10,
                    'Explicit': [True, False] * 15
                }

                df_demo = pd.DataFrame(demo_data)
                dataset_path.parent.mkdir(exist_ok=True)
                df_demo.to_csv(dataset_path, index=False)

                st.success("✅ Dataset demo creado")
                st.rerun()

            except Exception as e:
                st.error(f"Error: {e}")

    return None
