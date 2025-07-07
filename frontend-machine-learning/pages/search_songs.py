"""
Página para buscar canciones en el dataset
Versión mejorada con carrusel horizontal e integración Spotify
"""

import streamlit as st
import math
import requests
import urllib.parse
import concurrent.futures
import threading
from typing import Dict, Any, List
from utils.data_manager import search_songs_paginated, data_manager
from utils.ml_functions import analyze_words

# CSS personalizado para carrusel y tarjetas mejoradas
def inject_custom_css():
    """Inyectar CSS personalizado para el carrusel y diseño mejorado"""
    st.markdown("""
    <style>
        /* Carrusel horizontal */
        .songs-carousel {
            display: flex;
            overflow-x: auto;
            gap: 20px;
            padding: 20px 0;
            scroll-behavior: smooth;
        }

        .songs-carousel::-webkit-scrollbar {
            height: 8px;
        }

        .songs-carousel::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }

        .songs-carousel::-webkit-scrollbar-thumb {
            background: #1f77b4;
            border-radius: 10px;
        }

        /* Tarjeta de canción mejorada */
        .song-card-enhanced {
            min-width: 280px;
            max-width: 280px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 20px;
            color: white;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            position: relative;
            overflow: hidden;
            cursor: pointer;
            border: 3px solid transparent;
        }

        .song-card-enhanced:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 35px rgba(0,0,0,0.25);
        }

        .song-card-enhanced.selected {
            background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%);
            box-shadow: 0 12px 35px rgba(255,107,107,0.4);
            transform: scale(1.02);
            border: 3px solid #fff;
        }

        .song-card-enhanced.selected::after {
            content: '✓';
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(255,255,255,0.9);
            color: #ff6b6b;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.2rem;
        }

        .song-card-enhanced::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255,255,255,0.1);
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .song-card-enhanced:hover::before {
            opacity: 1;
        }

        /* Imagen del álbum */
        .album-image {
            width: 100%;
            height: 180px;
            object-fit: cover;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            display: none; /* Oculto por defecto, se muestra cuando carga */
        }

        .album-placeholder {
            width: 100%;
            height: 180px;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3rem;
            margin-bottom: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }

        /* Mostrar imagen cuando carga exitosamente */
        .song-card-enhanced img.album-image[style*="display: block"] + .album-placeholder {
            display: none;
        }

        /* Textos de la tarjeta */
        .card-title {
            font-size: 1.1rem;
            font-weight: bold;
            margin-bottom: 8px;
            line-height: 1.3;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            color: white;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }

        .card-artist {
            font-size: 0.9rem;
            opacity: 0.9;
            margin-bottom: 10px;
            color: #f0f0f0;
        }

        .card-genre {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 4px 8px;
            border-radius: 20px;
            font-size: 0.8rem;
            margin-bottom: 10px;
            backdrop-filter: blur(10px);
        }

        /* Badges mejorados */
        .explicit-badge-enhanced {
            background: #ff4757;
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
            display: inline-block;
            margin: 5px 0;
            box-shadow: 0 2px 8px rgba(255,71,87,0.3);
        }

        .clean-badge-enhanced {
            background: #2ed573;
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
            display: inline-block;
            margin: 5px 0;
            box-shadow: 0 2px 8px rgba(46,213,115,0.3);
        }

        /* Botones de acción - removidos porque usamos botones de Streamlit */

        /* Información adicional */
        .card-metadata {
            font-size: 0.7rem;
            opacity: 0.8;
            margin-top: 10px;
            line-height: 1.4;
        }

        /* Indicador de similitud */
        .similarity-score {
            position: absolute;
            top: 15px;
            right: 15px;
            background: rgba(255,255,255,0.9);
            color: #333;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: bold;
        }

        /* Contenedor del carrusel */
        .carousel-container {
            background: rgba(255,255,255,0.02);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            border: 1px solid rgba(255,255,255,0.1);
        }

        .carousel-title {
            font-size: 1.3rem;
            font-weight: bold;
            margin-bottom: 20px;
            color: #333;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .song-card-enhanced {
                min-width: 250px;
                max-width: 250px;
            }

            .album-image, .album-placeholder {
                height: 150px;
            }
        }
    </style>
    """, unsafe_allow_html=True)

def show_search_page():
    """Mostrar la página de búsqueda de canciones"""

    # Inyectar CSS personalizado
    inject_custom_css()

    st.title("🔍 Buscar Canciones")
    st.markdown("Explora el dataset de canciones y analiza su contenido explícito")

    # Formulario de búsqueda
    with st.form("search_form"):
        col1, col2 = st.columns(2)

        with col1:
            title_query = st.text_input(
                "🎵 Título de la canción",
                placeholder="Ej: Blinding Lights",
                help="Busca por título de canción (búsqueda parcial)"
            )

        with col2:
            artist_query = st.text_input(
                "🎤 Artista",
                placeholder="Ej: The Weeknd",
                help="Busca por nombre del artista (búsqueda parcial)"
            )

        search_button = st.form_submit_button("🔍 Buscar", use_container_width=True)

    # Inicializar estado de la sesión
    if 'search_page' not in st.session_state:
        st.session_state.search_page = 1
    if 'search_title' not in st.session_state:
        st.session_state.search_title = ""
    if 'search_artist' not in st.session_state:
        st.session_state.search_artist = ""
    if 'search_genre' not in st.session_state:
        st.session_state.search_genre = ""

    # Si se hizo una nueva búsqueda, resetear página y selección
    if search_button:
        st.session_state.search_page = 1
        st.session_state.search_title = title_query
        st.session_state.search_artist = artist_query
        st.session_state.search_genre = ""  # Limpiar búsqueda por género al hacer búsqueda manual
        st.session_state.selected_song_index = None  # Limpiar selección
        st.rerun()

    # Usar valores de la sesión para mantener la búsqueda
    current_title = st.session_state.search_title
    current_artist = st.session_state.search_artist
    current_genre = st.session_state.search_genre
    current_page = st.session_state.search_page

    # Realizar búsqueda
    if current_title or current_artist or current_genre:
        with st.spinner("Buscando canciones..."):
            if current_genre:
                # Usar búsqueda por género
                from utils.data_manager import search_songs_by_genre_paginated
                songs, total_results, total_pages = search_songs_by_genre_paginated(
                    genre_query=current_genre,
                    page=current_page,
                    per_page=10
                )
            else:
                # Usar búsqueda tradicional por título y artista
                songs, total_results, total_pages = search_songs_paginated(
                    title_query=current_title,
                    artist_query=current_artist,
                    page=current_page,
                    per_page=10
                )

        # Mostrar resultados
        if total_results > 0:
            st.markdown(f"### 📊 Resultados: {total_results:,} canciones encontradas")

            # Determinar si mostrar acciones (solo para búsquedas específicas)
            show_actions = should_show_actions(current_title, current_artist, current_genre, total_results)

            # Mostrar carrusel de canciones directamente (sin contenedores extra)
            show_songs_carousel(songs, current_page, show_actions)

            # Paginación
            if total_pages > 1:
                show_pagination(current_page, total_pages)

        else:
            st.warning("No se encontraron canciones con esos criterios de búsqueda.")
            st.markdown("**Sugerencias:**")
            st.markdown("- Verifica la ortografía")
            st.markdown("- Usa menos palabras específicas")
            st.markdown("- Prueba con búsquedas parciales")

    else:
        # Mostrar canciones populares o sugerencias
        show_popular_songs()

def get_fallback_image_url(song_title: str, artist: str) -> str:
    """
    Generar URL de imagen placeholder usando un servicio externo

    Args:
        song_title: Título de la canción
        artist: Artista

    Returns:
        URL de imagen placeholder
    """
    # Usar diferentes colores basados en el hash del título
    hash_val = hash(song_title) % 6
    colors = [
        "667eea",  # Azul-Púrpura
        "ff6b6b",  # Rojo
        "a8edea",  # Verde agua
        "ffecd2",  # Amarillo-Naranja
        "cbb4d4",  # Púrpura claro
        "4ecdc4"   # Verde azulado
    ]

    color = colors[hash_val]

    # Usar un texto más simple para evitar problemas de codificación
    text = "Music"

    # Generar imagen con texto usando placeholder.com con formato correcto
    return f"https://via.placeholder.com/300x300/{color}/ffffff?text={text}"

def get_spotify_info_batch(songs: List[Dict[str, Any]], enable_api_calls: bool = True) -> Dict[str, Dict[str, Any]]:
    """
    Obtener información de Spotify para múltiples canciones de forma optimizada

    Args:
        songs: Lista de canciones
        enable_api_calls: Si realizar llamadas a la API (False para búsquedas amplias)

    Returns:
        Diccionario con información de Spotify por canción (clave: "title::artist")
    """
    spotify_info = {}

    # Para búsquedas amplias o cuando API está deshabilitada, usar solo placeholders
    if not enable_api_calls or len(songs) > 8:
        for song in songs:
            key = f"{song['title']}::{song['artist']}"
            spotify_info[key] = {
                "image_url": get_fallback_image_url(song['title'], song['artist']),
                "album_name": f"Album de {song['artist']}",
                "release_date": "2020",
                "popularity": hash(song['title']) % 100,
                "preview_url": None
            }
        return spotify_info

    # Para búsquedas específicas (8 o menos canciones), intentar API real
    try:
        def fetch_single_song_info(song):
            """Función auxiliar para obtener info de una canción individual"""
            try:
                response = requests.post(
                    "http://localhost:8000/search-spotify",
                    json={"query": f"{song['title']} {song['artist']}", "limit": 1},
                    timeout=3
                )

                key = f"{song['title']}::{song['artist']}"

                if response.status_code == 200:
                    data = response.json()
                    if data.get("results") and data["results"][0].get("spotify_info"):
                        return key, data["results"][0]["spotify_info"]

                # Fallback si no hay datos de API
                return key, {
                    "image_url": get_fallback_image_url(song['title'], song['artist']),
                    "album_name": f"Album de {song['artist']}",
                    "release_date": "2020",
                    "popularity": hash(song['title']) % 100,
                    "preview_url": None
                }

            except Exception:
                key = f"{song['title']}::{song['artist']}"
                return key, {
                    "image_url": get_fallback_image_url(song['title'], song['artist']),
                    "album_name": f"Album de {song['artist']}",
                    "release_date": "2020",
                    "popularity": hash(song['title']) % 100,
                    "preview_url": None
                }

        # Usar ThreadPoolExecutor para paralelizar las llamadas
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_song = {executor.submit(fetch_single_song_info, song): song for song in songs}

            for future in concurrent.futures.as_completed(future_to_song, timeout=10):
                try:
                    key, info = future.result()
                    spotify_info[key] = info
                except Exception:
                    # En caso de timeout o error individual, usar fallback
                    song = future_to_song[future]
                    key = f"{song['title']}::{song['artist']}"
                    spotify_info[key] = {
                        "image_url": get_fallback_image_url(song['title'], song['artist']),
                        "album_name": f"Album de {song['artist']}",
                        "release_date": "2020",
                        "popularity": hash(song['title']) % 100,
                        "preview_url": None
                    }

    except Exception:
        # Fallback completo en caso de error general
        for song in songs:
            key = f"{song['title']}::{song['artist']}"
            spotify_info[key] = {
                "image_url": get_fallback_image_url(song['title'], song['artist']),
                "album_name": f"Album de {song['artist']}",
                "release_date": "2020",
                "popularity": hash(song['title']) % 100,
                "preview_url": None
            }

    return spotify_info

def get_spotify_info_from_api(song_name: str, artist_name: str) -> Dict[str, Any]:
    """
    Función mantenida para compatibilidad - ahora usa fallback directo

    Args:
        song_name: Nombre de la canción
        artist_name: Nombre del artista

    Returns:
        Información de Spotify o datos simulados
    """
    return {
        "image_url": get_fallback_image_url(song_name, artist_name),
        "album_name": f"Album de {artist_name}",
        "release_date": "2020",
        "popularity": hash(song_name) % 100,
        "preview_url": None
    }

def should_show_actions(title: str, artist: str, genre: str, total_results: int) -> bool:
    """
    Determina si mostrar los botones de acción basado en la especificidad de la búsqueda.

    Args:
        title: Título de la canción buscada
        artist: Artista buscado
        genre: Género buscado
        total_results: Número total de resultados

    Returns:
        True si se deben mostrar las acciones, False en caso contrario
    """
    # Si hay tanto título como artista, la búsqueda es específica
    if title and artist:
        # Si hay solo 1 resultado, mostrar acciones directamente
        if total_results == 1:
            return True
        # Si hay múltiples resultados, usar sistema de selección individual
        else:
            return "selection_mode"

    # Si solo hay uno de los campos y pocos resultados (máximo 5), mostrar acciones
    if (title or artist) and total_results <= 5:
        return True

    # Para búsquedas por género, usar modo de selección si hay resultados manejables
    if genre and total_results <= 20:
        return "selection_mode"

    # Para búsquedas muy amplias, no mostrar acciones
    return False

def show_selected_song_actions(song: Dict[str, Any], song_index: int):
    """
    Mostrar acciones para la canción seleccionada

    Args:
        song: Diccionario con información de la canción seleccionada
        song_index: Índice global de la canción
    """
    st.markdown("---")
    st.markdown(f"### 🎯 Canción Seleccionada: **{song['title']}** - *{song['artist']}*")

    # Mostrar información básica de la canción seleccionada
    col_info1, col_info2, col_info3 = st.columns(3)

    with col_info1:
        if song.get('genre') and song['genre'] != 'Desconocido':
            st.markdown(f"**Género:** {song['genre']}")
        else:
            st.markdown("**Género:** No disponible")

    with col_info2:
        if song.get('is_explicit', False):
            st.markdown("**Contenido:** 🔥 Explícita")
        else:
            st.markdown("**Contenido:** ✅ Limpia")

    with col_info3:
        # Mostrar alguna info adicional si está disponible
        if song.get('album'):
            st.markdown(f"**Álbum:** {song['album']}")
        else:
            st.markdown("**Álbum:** No disponible")

    # Botones de acción para la canción seleccionada
    st.markdown("#### 🎛️ Acciones Disponibles")

    action_col1, action_col2, action_col3, action_col4 = st.columns([2, 2, 2, 2])

    with action_col1:
        if st.button("📝 Analizar Letra", key=f"selected_analyze_{song_index}", use_container_width=True, type="primary"):
            st.session_state[f'analyze_song_{song_index}'] = song
            st.rerun()

    with action_col2:
        if st.button("💡 Canciones Similares", key=f"selected_similar_{song_index}", use_container_width=True, type="primary"):
            get_song_recommendations(song)

    with action_col3:
        if st.button("👁️ Ver Letra Completa", key=f"selected_view_{song_index}", use_container_width=True, type="primary"):
            st.session_state[f'view_lyrics_{song_index}'] = song
            st.rerun()

    with action_col4:
        if st.button("❌ Deseleccionar", key=f"deselect_{song_index}", use_container_width=True, type="secondary"):
            st.session_state.selected_song_index = None
            st.rerun()

def show_songs_carousel(songs: List[Dict[str, Any]], page: int, show_actions):
    """
    Mostrar canciones en formato carrusel horizontal

    Args:
        songs: Lista de canciones
        page: Página actual
        show_actions: Si mostrar botones de acción (True/False/"selection_mode")
    """
    st.markdown('<div class="carousel-title">🎵 Resultados de Búsqueda</div>', unsafe_allow_html=True)

    # Inicializar estado de selección si no existe
    if 'selected_song_index' not in st.session_state:
        st.session_state.selected_song_index = None

    # Mostrar indicador de carga para búsquedas específicas (pocas canciones con acciones habilitadas)
    if show_actions != False and len(songs) <= 8:
        with st.spinner('🎵 Obteniendo información de Spotify...'):
            spotify_info_batch = get_spotify_info_batch(songs, enable_api_calls=True)
    else:
        # Para búsquedas amplias, usar placeholders inmediatamente (sin carga ni API calls)
        spotify_info_batch = get_spotify_info_batch(songs, enable_api_calls=False)

    # Debug: Mostrar información sobre las imágenes (solo en modo debug)
    if len(songs) <= 3:  # Solo para pocas canciones para no saturar
        for song in songs[:2]:  # Solo primeras 2 canciones
            key = f"{song['title']}::{song['artist']}"
            info = spotify_info_batch.get(key, {})
            if info.get('image_url'):
                st.sidebar.write(f"🖼️ Debug - {song['title']}: {info['image_url'][:50]}...")

    # Crear el carrusel con capacidad de selección
    carousel_html = '<div class="songs-carousel">'

    for i, song in enumerate(songs):
        index = i + ((page - 1) * 10)

        # Obtener información de Spotify desde el batch
        key = f"{song['title']}::{song['artist']}"
        spotify_info = spotify_info_batch.get(key, {
            "image_url": get_fallback_image_url(song['title'], song['artist']),
            "album_name": f"Album de {song['artist']}",
            "release_date": "2020",
            "popularity": 50,
            "preview_url": None
        })

        # Verificar si esta canción está seleccionada
        is_selected = st.session_state.selected_song_index == index

        # Crear tarjeta HTML con selección
        card_html = create_enhanced_song_card(song, index, spotify_info, is_selected, show_actions == "selection_mode")
        carousel_html += card_html

    carousel_html += '</div>'
    st.markdown(carousel_html, unsafe_allow_html=True)

    # Manejar modo de selección
    if show_actions == "selection_mode":
        # Mostrar instrucciones
        if st.session_state.selected_song_index is None:
            st.info("👆 **Haz clic en una canción específica** para ver las opciones de análisis y recomendaciones.")

        # Crear botones de selección
        cols = st.columns(len(songs))
        for i, song in enumerate(songs):
            index = i + ((page - 1) * 10)
            with cols[i]:
                button_text = "✓ Seleccionada" if st.session_state.selected_song_index == index else f"Seleccionar #{i+1}"
                button_type = "secondary" if st.session_state.selected_song_index == index else "primary"

                if st.button(button_text, key=f"select_{index}", use_container_width=True, type=button_type):
                    if st.session_state.selected_song_index == index:
                        # Deseleccionar si ya está seleccionada
                        st.session_state.selected_song_index = None
                    else:
                        # Seleccionar nueva canción
                        st.session_state.selected_song_index = index
                    st.rerun()

        # Mostrar acciones solo si hay una canción seleccionada
        if st.session_state.selected_song_index is not None:
            selected_song_local_index = st.session_state.selected_song_index - ((page - 1) * 10)
            if 0 <= selected_song_local_index < len(songs):
                selected_song = songs[selected_song_local_index]
                show_selected_song_actions(selected_song, st.session_state.selected_song_index)

    # Botones de acción tradicionales (para casos sin modo de selección)
    elif show_actions == True:
        st.markdown("### 🎛️ Acciones")

        cols = st.columns(len(songs))
        for i, song in enumerate(songs):
            index = i + ((page - 1) * 10)
            with cols[i]:
                if st.button("📝 Analizar", key=f"analyze_{index}", use_container_width=True):
                    st.session_state[f'analyze_song_{index}'] = song
                    st.rerun()

                if st.button("💡 Similares", key=f"similar_{index}", use_container_width=True):
                    get_song_recommendations(song)

                if st.button("👁️ Ver Letra", key=f"view_{index}", use_container_width=True):
                    st.session_state[f'view_lyrics_{index}'] = song
                    st.rerun()
    else:
        st.info("💡 **Sugerencia**: Para acceder a análisis y recomendaciones, busca una canción específica con título y artista.")

    st.markdown('</div>', unsafe_allow_html=True)

    # Mostrar análisis si fue solicitado (para ambos modos)
    if show_actions in [True, "selection_mode"]:
        for i, song in enumerate(songs):
            index = i + ((page - 1) * 10)
            if st.session_state.get(f'analyze_song_{index}'):
                analyze_song_lyrics(st.session_state[f'analyze_song_{index}'])
                del st.session_state[f'analyze_song_{index}']

            if st.session_state.get(f'view_lyrics_{index}'):
                show_lyrics_preview(st.session_state[f'view_lyrics_{index}'])
                del st.session_state[f'view_lyrics_{index}']

    # Mostrar acciones solo para la canción seleccionada (ya se manejan en las tarjetas individuales)
    # Pero mantener el procesamiento de análisis y visualización de letras
    for i, song in enumerate(songs):
        index = i + ((page - 1) * 10)
        if st.session_state.get(f'analyze_song_{index}'):
            analyze_song_lyrics(st.session_state[f'analyze_song_{index}'])
            del st.session_state[f'analyze_song_{index}']

        if st.session_state.get(f'view_lyrics_{index}'):
            show_lyrics_preview(st.session_state[f'view_lyrics_{index}'])
            del st.session_state[f'view_lyrics_{index}']

def create_enhanced_song_card(song: Dict[str, Any], index: int, spotify_info: Dict[str, Any] = None, is_selected: bool = False, is_selectable: bool = False) -> str:
    """
    Crear HTML para una tarjeta de canción mejorada

    Args:
        song: Diccionario con información de la canción
        index: Índice de la canción
        spotify_info: Información de Spotify opcional
        is_selected: Si la tarjeta está seleccionada

    Returns:
        HTML de la tarjeta
    """
    # Imagen del álbum - lógica simplificada
    image_html = ""
    placeholder_html = '<div class="album-placeholder">🎵</div>'

    # Si hay información de Spotify y es una URL real de imagen (no placeholder)
    if (spotify_info and
        spotify_info.get("image_url") and
        not spotify_info["image_url"].startswith("https://via.placeholder.com") and
        spotify_info["image_url"].startswith(("https://", "http://"))):

        image_html = f'<img src="{spotify_info["image_url"]}" class="album-image" alt="Album cover" onload="this.style.display=\'block\'; this.parentElement.querySelector(\'.album-placeholder\').style.display=\'none\';" onerror="this.style.display=\'none\'; this.parentElement.querySelector(\'.album-placeholder\').style.display=\'flex\';"/>'

    # Siempre incluir placeholder
    image_html += placeholder_html

    # Badge de explícito/limpio
    if song.get('is_explicit', False):
        badge_html = '<div class="explicit-badge-enhanced">🔥 EXPLÍCITA</div>'
    else:
        badge_html = '<div class="clean-badge-enhanced">✅ LIMPIA</div>'

    # Género
    genre_html = ""
    if song.get('genre') and song['genre'] != 'Desconocido':
        genre_html = f'<div class="card-genre">{song["genre"]}</div>'

    # Información adicional de Spotify
    metadata_html = ""
    if spotify_info:
        metadata_items = []
        if spotify_info.get("album_name"):
            metadata_items.append(f"📀 {spotify_info['album_name']}")
        if spotify_info.get("release_date"):
            metadata_items.append(f"📅 {spotify_info['release_date']}")
        if spotify_info.get("popularity"):
            metadata_items.append(f"🔥 {spotify_info['popularity']}% popularidad")

        if metadata_items:
            metadata_html = f'<div class="card-metadata">{"<br>".join(metadata_items)}</div>'

    # Escapar contenido para HTML
    title = song.get("title", "Sin título").replace("'", "&#39;").replace('"', "&quot;").replace('<', '&lt;').replace('>', '&gt;')
    artist = song.get("artist", "Artista desconocido").replace("'", "&#39;").replace('"', "&quot;").replace('<', '&lt;').replace('>', '&gt;')

    # Crear HTML sin saltos de línea para evitar problemas de renderizado
    selected_class = " selected" if is_selected else ""

    card_html = f'<div class="song-card-enhanced{selected_class}" data-index="{index}">{image_html}<div class="card-title">{title}</div><div class="card-artist">por {artist}</div>{genre_html}{badge_html}{metadata_html}</div>'

    return card_html

def get_song_recommendations(song: Dict[str, Any]):
    """
    Obtener y mostrar recomendaciones para una canción

    Args:
        song: Diccionario con información de la canción
    """
    st.markdown(f"### 💡 Canciones similares a: {song['title']} - {song['artist']}")

    with st.spinner("Buscando canciones similares..."):
        try:
            response = requests.post(
                "http://localhost:8000/recommend",
                json={
                    "song_name": song["title"],
                    "artist_name": song["artist"],
                    "max_recommendations": 6
                },
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                recommendations = data["recommendations"]

                if recommendations:
                    st.success(f"Encontradas {len(recommendations)} canciones similares")

                    # Mostrar recomendaciones en carrusel
                    show_recommendations_carousel(recommendations)

                else:
                    st.info("No se encontraron canciones similares en este momento.")

            else:
                st.error(f"Error al obtener recomendaciones: {response.status_code}")

        except requests.exceptions.ConnectionError:
            st.error("No se pudo conectar con el sistema de recomendaciones. Asegúrate de que la API esté funcionando.")
        except Exception as e:
            st.error(f"Error inesperado: {e}")

def show_recommendations_carousel(recommendations: List[Dict[str, Any]]):
    """
    Mostrar recomendaciones en formato carrusel

    Args:
        recommendations: Lista de recomendaciones
    """
    st.markdown('<div class="carousel-container">', unsafe_allow_html=True)

    carousel_html = '<div class="songs-carousel">'

    for i, rec in enumerate(recommendations):
        # Crear tarjeta con score de similitud
        card_html = create_recommendation_card(rec, i)
        carousel_html += card_html

    carousel_html += '</div>'
    st.markdown(carousel_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def create_recommendation_card(recommendation: Dict[str, Any], index: int) -> str:
    """
    Crear tarjeta HTML para una recomendación

    Args:
        recommendation: Diccionario con información de la recomendación
        index: Índice de la recomendación (no usado pero mantenido para compatibilidad)

    Returns:
        HTML de la tarjeta
    """
    # Generar URL de imagen placeholder con colores únicos
    def get_fallback_image_url(song_title: str, artist: str) -> str:
        hash_val = hash(song_title) % 6
        colors = ["667eea", "ff6b6b", "a8edea", "ffecd2", "cbb4d4", "4ecdc4"]
        color = colors[hash_val]
        return f"https://via.placeholder.com/300x300/{color}/ffffff?text=Music"

    # Información de Spotify si está disponible - simplificado
    spotify_info = recommendation.get("spotify_info")

    # Manejo simplificado de imágenes
    if (spotify_info and
        spotify_info.get("image_url") and
        spotify_info["image_url"].startswith(("https://", "http://")) and
        not spotify_info["image_url"].startswith("https://via.placeholder.com")):

        # Usar imagen real de Spotify
        image_html = f'<img src="{spotify_info["image_url"]}" class="album-image" alt="Album cover">'
    else:
        # Usar placeholder colorido
        fallback_url = get_fallback_image_url(recommendation.get("song", ""), recommendation.get("artist", ""))
        image_html = f'<img src="{fallback_url}" class="album-image" alt="Album cover">'

    # Score de similitud
    similarity_score = recommendation.get("similarity_score", 0)
    similarity_html = f'<div class="similarity-score">{similarity_score:.2f}</div>'

    # Badge de explícito/limpio - maneja tanto 'explicit' (API) como 'is_explicit' (dataset local)
    is_explicit = recommendation.get('explicit', recommendation.get('is_explicit', False))
    if is_explicit:
        badge_html = '<div class="explicit-badge-enhanced">🔥 EXPLÍCITA</div>'
    else:
        badge_html = '<div class="clean-badge-enhanced">✅ LIMPIA</div>'

    # Género
    genre_html = ""
    if recommendation.get('genre'):
        genre_html = f'<div class="card-genre">{recommendation["genre"]}</div>'

    # Escapar contenido para HTML
    song_name = recommendation.get("song", "Sin título").replace("'", "&#39;").replace('"', "&quot;").replace('<', '&lt;').replace('>', '&gt;')
    artist_name = recommendation.get("artist", "Artista desconocido").replace("'", "&#39;").replace('"', "&quot;").replace('<', '&lt;').replace('>', '&gt;')

    # Crear HTML simplificado
    card_html = f'<div class="song-card-enhanced">{similarity_html}{image_html}<div class="card-title">{song_name}</div><div class="card-artist">por {artist_name}</div>{genre_html}{badge_html}</div>'

    return card_html

def show_song_card(song: Dict[str, Any], index: int):
    """
    Mostrar una tarjeta de canción (versión original - mantenida para compatibilidad)

    Args:
        song: Diccionario con información de la canción
        index: Índice de la canción en la lista
    """
    with st.container():
        # Header de la tarjeta
        col1, col2 = st.columns([3, 1])

        with col1:
            # Título y artista
            st.markdown(f'<div class="song-title">{song["title"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="song-artist">por {song["artist"]}</div>', unsafe_allow_html=True)

        with col2:
            # Badge de explícito/limpio
            if song['is_explicit']:
                st.markdown('<span class="explicit-badge">🔥 EXPLÍCITA</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="clean-badge">✅ LIMPIA</span>', unsafe_allow_html=True)

        # Género
        if song.get('genre') and song['genre'] != 'Desconocido':
            st.markdown(f'<span class="song-genre">{song["genre"]}</span>', unsafe_allow_html=True)

        # Botón para analizar
        col_a, col_b, _ = st.columns([1, 1, 2])

        with col_a:
            if st.button("📝 Analizar", key=f"analyze_{index}"):
                analyze_song_lyrics(song)

        with col_b:
            if st.button("👁️ Ver Letra", key=f"view_{index}"):
                show_lyrics_preview(song)

        st.markdown("---")

def analyze_song_lyrics(song: Dict[str, Any]):
    """
    Analizar las letras de una canción con el modelo

    Args:
        song: Diccionario con información de la canción
    """
    st.markdown(f"### 🔬 Análisis: {song['title']} - {song['artist']}")

    with st.spinner("Analizando letras con IA..."):
        analysis = analyze_words(
            lyrics=song['lyrics'],
            song_title=song['title'],
            artist=song['artist']
        )

    if analysis and "error" not in analysis:
        # Predicción general
        overall = analysis
        confidence = overall.get('confidence', 0)
        confidence_text = f"{confidence:.1%}"

        col1, col2 = st.columns(2)

        with col1:
            if overall.get('is_explicit'):
                st.error(f"🔥 **CONTENIDO EXPLÍCITO** ({confidence_text})")
            else:
                st.success(f"✅ **CONTENIDO LIMPIO** ({confidence_text})")

        with col2:
            st.metric(
                "Confianza del Modelo",
                confidence_text,
                help="Qué tan seguro está el modelo de su predicción"
            )

        # Análisis de palabras
        st.markdown("#### 🔍 Análisis por Palabra")

        explicit_words = analysis.get('explicit_words', [])

        if explicit_words:
            st.markdown("**Palabras identificadas como explícitas:**")

            # Mostrar palabras explícitas en filas
            cols_per_row = 4
            for i in range(0, len(explicit_words), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, word in enumerate(explicit_words[i:i+cols_per_row]):
                    with cols[j]:
                        st.markdown(
                            f'<span class="explicit-word">{word}</span>',
                            unsafe_allow_html=True
                        )
        else:
            st.info("No se identificaron palabras explícitas específicas.")

        # Información adicional
        with st.expander("📊 Información Adicional"):
            col_a, col_b, col_c = st.columns(3)

            with col_a:
                word_count = analysis.get('word_count', 0)
                st.metric("Total Palabras", word_count)

            with col_b:
                explicit_count = len(explicit_words)
                st.metric("Palabras Explícitas", explicit_count)

            with col_c:
                percentage = (explicit_count / max(word_count, 1)) * 100
                st.metric("Porcentaje Explícito", f"{percentage:.1f}%")

    else:
        st.error("Error al analizar la canción. Verifica que el modelo ML esté funcionando.")

def show_lyrics_preview(song: Dict[str, Any]):
    """
    Mostrar preview de las letras

    Args:
        song: Diccionario con información de la canción
    """
    st.markdown(f"### 📜 Letra: {song['title']} - {song['artist']}")

    lyrics = song['lyrics']

    st.text_area(
        "Letra completa:",
        value=lyrics,
        height=300,
        disabled=True
    )

    if song['is_explicit']:
        st.warning("⚠️ Esta canción contiene contenido explícito según el dataset original.")
    else:
        st.info("ℹ️ Esta canción está marcada como contenido limpio en el dataset original.")

def show_pagination(current_page: int, total_pages: int):
    """
    Mostrar controles de paginación

    Args:
        current_page: Página actual
        total_pages: Total de páginas
    """
    st.markdown("---")
    st.markdown(f"**Página {current_page} de {total_pages}**")

    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

    with col1:
        if st.button("⏮️ Primera", key="pagination_first", disabled=current_page == 1):
            st.session_state.search_page = 1
            st.session_state.selected_song_index = None  # Limpiar selección
            st.rerun()

    with col2:
        if st.button("⬅️ Anterior", key="pagination_prev", disabled=current_page == 1):
            st.session_state.search_page = current_page - 1
            st.session_state.selected_song_index = None  # Limpiar selección
            st.rerun()

    with col4:
        if st.button("➡️ Siguiente", key="pagination_next", disabled=current_page == total_pages):
            st.session_state.search_page = current_page + 1
            st.session_state.selected_song_index = None  # Limpiar selección
            st.rerun()

    with col5:
        if st.button("⏭️ Última", key="pagination_last", disabled=current_page == total_pages):
            st.session_state.search_page = total_pages
            st.session_state.selected_song_index = None  # Limpiar selección
            st.rerun()

def show_popular_songs():
    """Mostrar canciones populares o sugerencias cuando no hay búsqueda"""
    st.markdown("### 🎵 Explora el Dataset")
    st.markdown("Utiliza el formulario de búsqueda para encontrar canciones específicas.")

    # Mostrar estadísticas del dataset
    df = data_manager.get_dataset()
    if df is not None and not df.empty:
        total_songs = len(df)
        # Usar la columna correcta is_explicit (booleana)
        explicit_songs = df['is_explicit'].sum() if 'is_explicit' in df.columns else 0
        clean_songs = total_songs - explicit_songs

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("📊 Total Canciones", f"{total_songs:,}")

        with col2:
            st.metric("🔥 Explícitas", f"{explicit_songs:,}")

        with col3:
            st.metric("✅ Limpias", f"{clean_songs:,}")

        # Sugerencias de búsqueda
        st.markdown("### 💡 Sugerencias de Búsqueda")

        suggestion_cols = st.columns(3)

        with suggestion_cols[0]:
            if st.button("🎸 Rock/Metal", key="genre_rock", use_container_width=True):
                st.session_state.search_title = ""
                st.session_state.search_artist = ""
                st.session_state.search_genre = "rock"
                st.session_state.search_page = 1
                st.rerun()

        with suggestion_cols[1]:
            if st.button("🎤 Hip Hop", key="genre_hiphop", use_container_width=True):
                st.session_state.search_title = ""
                st.session_state.search_artist = ""
                st.session_state.search_genre = "hip hop"
                st.session_state.search_page = 1
                st.rerun()

        with suggestion_cols[2]:
            if st.button("💿 Pop", key="genre_pop", use_container_width=True):
                st.session_state.search_title = ""
                st.session_state.search_artist = ""
                st.session_state.search_genre = "pop"
                st.session_state.search_page = 1
                st.rerun()

def show_clickable_song_card(song: Dict[str, Any], song_local_index: int, page: int, spotify_info_batch: Dict[str, Dict[str, Any]]):
    """
    Mostrar una tarjeta de canción clickeable usando componentes de Streamlit

    Args:
        song: Diccionario con información de la canción
        song_local_index: Índice local de la canción en la página actual
        page: Página actual
        spotify_info_batch: Información de Spotify para todas las canciones
    """
    # Calcular índice global
    global_index = song_local_index + ((page - 1) * 10)

    # Obtener información de Spotify
    key = f"{song['title']}::{song['artist']}"
    spotify_info = spotify_info_batch.get(key, {
        "image_url": get_fallback_image_url(song['title'], song['artist']),
        "album_name": f"Album de {song['artist']}",
        "release_date": "2020",
        "popularity": 50,
        "preview_url": None
    })

    # Verificar si está seleccionada
    is_selected = st.session_state.selected_song_index == global_index

    # Crear contenedor de la tarjeta con estilo condicional
    if is_selected:
        # Tarjeta seleccionada con estilo destacado
        with st.container():
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%);
                    border-radius: 15px;
                    padding: 20px;
                    margin: 10px 0;
                    border: 3px solid #fff;
                    box-shadow: 0 12px 35px rgba(255,107,107,0.4);
                    color: white;
                ">
                    <h3 style="margin:0; color:white;">✅ {song['title']}</h3>
                    <p style="margin:5px 0; opacity:0.9;">por {song['artist']}</p>
                    <div style="margin:10px 0;">
                        {'🔥 EXPLÍCITA' if song.get('is_explicit', False) else '✅ LIMPIA'}
                    </div>
                    {f'<small style="opacity:0.8;">{song["genre"]}</small>' if song.get('genre') and song['genre'] != 'Desconocido' else ''}
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        # Tarjeta normal
        with st.container():
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 15px;
                    padding: 20px;
                    margin: 10px 0;
                    border: 3px solid transparent;
                    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
                    color: white;
                    transition: all 0.3s ease;
                ">
                    <h3 style="margin:0; color:white;">{song['title']}</h3>
                    <p style="margin:5px 0; opacity:0.9;">por {song['artist']}</p>
                    <div style="margin:10px 0;">
                        {'� EXPLÍCITA' if song.get('is_explicit', False) else '✅ LIMPIA'}
                    </div>
                    {f'<small style="opacity:0.8;">{song["genre"]}</small>' if song.get('genre') and song['genre'] != 'Desconocido' else ''}
                </div>
                """,
                unsafe_allow_html=True
            )

    # Botón principal de selección
    button_style = "secondary" if is_selected else "primary"
    button_text = "✓ SELECCIONADA" if is_selected else "🎵 SELECCIONAR"

    if st.button(button_text, key=f"card_select_{global_index}", use_container_width=True, type=button_style):
        if st.session_state.selected_song_index == global_index:
            # Deseleccionar
            st.session_state.selected_song_index = None
        else:
            # Seleccionar
            st.session_state.selected_song_index = global_index
        st.rerun()

    # Mostrar acciones si está seleccionada
    if is_selected:
        st.markdown("#### 🎛️ Acciones:")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📝 Analizar", key=f"analyze_card_{global_index}", use_container_width=True):
                st.session_state[f'analyze_song_{global_index}'] = song
                st.rerun()

        with col2:
            if st.button("💡 Similares", key=f"similar_card_{global_index}", use_container_width=True):
                get_song_recommendations(song)

        with col3:
            if st.button("👁️ Ver Letra", key=f"lyrics_card_{global_index}", use_container_width=True):
                st.session_state[f'view_lyrics_{global_index}'] = song
                st.rerun()

    # Separador visual
    st.markdown("---")
