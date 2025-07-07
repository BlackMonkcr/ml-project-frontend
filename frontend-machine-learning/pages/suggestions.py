"""
Página de sugerencias de canciones - Sistema de recomendaciones
Implementación completa con Word2Vec y similitud coseno
"""

import streamlit as st
import requests
from typing import Dict, Any, List

def show_suggestions_page():
    """Mostrar la página de sugerencias mejorada"""

    # CSS personalizado para sugerencias
    inject_suggestions_css()

    st.title("💡 Sugerencias de Canciones")
    st.markdown("Sistema de recomendaciones inteligente basado en análisis de letras con IA")

    # Formulario principal de búsqueda
    with st.form("recommendation_form"):
        st.markdown("### 🎵 Buscar Canciones Similares")

        col1, col2 = st.columns([2, 1])

        with col1:
            song_name = st.text_input(
                "🎤 Nombre de la canción",
                placeholder="Ej: Blinding Lights, Shape of You, Bohemian Rhapsody...",
                help="Escribe el nombre de una canción para encontrar canciones similares"
            )

        with col2:
            artist_name = st.text_input(
                "🎸 Artista (opcional)",
                placeholder="Ej: The Weeknd, Ed Sheeran...",
                help="Nombre del artista para mejorar la búsqueda"
            )

        max_recommendations = st.slider(
            "📊 Número de recomendaciones",
            min_value=3,
            max_value=12,
            value=6,
            help="Cantidad de canciones similares a mostrar"
        )

        get_recommendations = st.form_submit_button(
            "🔍 Obtener Recomendaciones",
            use_container_width=True
        )

    # Procesar recomendaciones
    if get_recommendations and song_name.strip():
        get_and_show_recommendations(song_name.strip(), artist_name.strip(), max_recommendations)
    elif get_recommendations:
        st.error("Por favor, ingresa el nombre de una canción.")

    # Mostrar información del sistema
    show_system_info()

    # Ejemplos populares
    show_popular_examples()

def inject_suggestions_css():
    """Inyectar CSS personalizado para la página de sugerencias"""
    st.markdown("""
    <style>
        /* Contenedor de recomendaciones */
        .recommendations-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
            color: white;
        }

        .recommendations-title {
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 20px;
            text-align: center;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }

        /* Carrusel de recomendaciones */
        .recs-carousel {
            display: flex;
            overflow-x: auto;
            gap: 20px;
            padding: 20px 0;
            scroll-behavior: smooth;
        }

        .recs-carousel::-webkit-scrollbar {
            height: 8px;
        }

        .recs-carousel::-webkit-scrollbar-track {
            background: rgba(255,255,255,0.2);
            border-radius: 10px;
        }

        .recs-carousel::-webkit-scrollbar-thumb {
            background: rgba(255,255,255,0.5);
            border-radius: 10px;
        }

        /* Tarjeta de recomendación */
        .rec-card {
            min-width: 250px;
            max-width: 250px;
            background: rgba(255,255,255,0.15);
            border-radius: 12px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            transition: all 0.3s ease;
        }

        .rec-card:hover {
            transform: translateY(-5px);
            background: rgba(255,255,255,0.25);
        }

        /* Imagen del álbum en recomendaciones */
        .rec-image {
            width: 100%;
            height: 160px;
            object-fit: cover;
            border-radius: 8px;
            margin-bottom: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }

        .rec-placeholder {
            width: 100%;
            height: 160px;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5rem;
            margin-bottom: 15px;
        }

        /* Textos de recomendación */
        .rec-title {
            font-size: 1rem;
            font-weight: bold;
            margin-bottom: 8px;
            line-height: 1.3;
            color: white;
        }

        .rec-artist {
            font-size: 0.85rem;
            opacity: 0.9;
            margin-bottom: 8px;
            color: #f0f0f0;
        }

        .rec-similarity {
            background: rgba(46, 213, 115, 0.8);
            color: white;
            padding: 4px 8px;
            border-radius: 15px;
            font-size: 0.75rem;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 8px;
        }

        .rec-genre {
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 3px 6px;
            border-radius: 10px;
            font-size: 0.7rem;
            display: inline-block;
        }

        /* Info del sistema */
        .system-info {
            background: rgba(0,0,0,0.02);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border: 1px solid rgba(0,0,0,0.1);
        }

        /* Ejemplos populares */
        .example-button {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 20px;
            margin: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .example-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
    </style>
    """, unsafe_allow_html=True)




def get_and_show_recommendations(song_name: str, artist_name: str, max_recommendations: int):
    """
    Obtener y mostrar recomendaciones de canciones usando dataset local

    Args:
        song_name: Nombre de la canción
        artist_name: Nombre del artista (opcional)
        max_recommendations: Número máximo de recomendaciones
    """
    with st.spinner("🔍 Buscando canciones similares..."):
        try:
            from utils.data_manager import get_suggestions, get_song_by_title_artist

            # Buscar la canción base
            base_song = get_song_by_title_artist(song_name, artist_name)

            if not base_song:
                st.error(f"❌ No se encontró la canción '{song_name}' en nuestra base de datos.")
                st.info("💡 **Sugerencias:**")
                st.markdown("- Verifica la ortografía del nombre")
                st.markdown("- Prueba con nombres más cortos o alternativos")
                st.markdown("- Incluye el nombre del artista para mejor precisión")
                show_fallback_suggestions()
                return

            # Obtener sugerencias
            recommendations = get_suggestions(song_name, artist_name)

            if recommendations:
                show_recommendations_results(base_song, recommendations[:max_recommendations])
            else:
                st.warning("No se encontraron recomendaciones específicas para esta canción.")
                show_fallback_suggestions()

        except Exception as e:
            st.error(f"❌ Error obteniendo recomendaciones: {str(e)}")
            show_fallback_suggestions()

def show_recommendations_results(base_song: Dict[str, Any], recommendations: List[Dict[str, Any]]):
    """
    Mostrar los resultados de recomendaciones

    Args:
        base_song: Información de la canción base
        recommendations: Lista de recomendaciones
    """
    # Información de la canción base
    st.success(f"✅ Canción encontrada: **{base_song['title']}** por **{base_song['artist']}**")

    if base_song.get('genre'):
        st.info(f"🎵 Género: {base_song['genre']}")

    # Contenedor de recomendaciones
    st.markdown('<div class="recommendations-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="recommendations-title">🎯 {len(recommendations)} Canciones Similares Encontradas</div>', unsafe_allow_html=True)

    # Crear carrusel de recomendaciones
    carousel_html = '<div class="recs-carousel">'

    for rec in recommendations:
        card_html = create_recommendation_card_html(rec)
        carousel_html += card_html

    carousel_html += '</div>'
    st.markdown(carousel_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Información adicional
    st.markdown("### 📊 Detalles de las Recomendaciones")

    # Estadísticas
    avg_similarity = sum(r.get('similarity_score', 0) for r in recommendations) / len(recommendations)
    explicit_count = sum(1 for r in recommendations if r.get('explicit', False))

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Similitud Promedio",
            f"{avg_similarity:.3f}",
            help="Puntuación promedio de similitud (0-1)"
        )

    with col2:
        st.metric(
            "Canciones Explícitas",
            f"{explicit_count}/{len(recommendations)}",
            help="Cantidad de canciones con contenido explícito"
        )

    with col3:
        genres = [r.get('genre', 'Desconocido') for r in recommendations if r.get('genre')]
        most_common_genre = max(set(genres), key=genres.count) if genres else 'Variado'
        st.metric(
            "Género Principal",
            most_common_genre,
            help="Género más común en las recomendaciones"
        )

def create_recommendation_card_html(recommendation: Dict[str, Any]) -> str:
    """
    Crear HTML para una tarjeta de recomendación

    Args:
        recommendation: Diccionario con información de la recomendación

    Returns:
        HTML de la tarjeta
    """
    # Información de Spotify si está disponible
    spotify_info = recommendation.get("spotify_info")

    # Generar URL de imagen placeholder con colores únicos
    def get_fallback_image_url(song_title: str, artist: str) -> str:
        hash_val = hash(song_title) % 6
        colors = ["667eea", "ff6b6b", "a8edea", "ffecd2", "cbb4d4", "4ecdc4"]
        color = colors[hash_val]
        return f"https://via.placeholder.com/300x300/{color}/ffffff?text=Music"

    # Manejo simplificado de imágenes
    if (spotify_info and
        spotify_info.get("image_url") and
        spotify_info["image_url"].startswith(("https://", "http://")) and
        not spotify_info["image_url"].startswith("https://via.placeholder.com")):

        # Usar imagen real de Spotify
        image_html = f'<img src="{spotify_info["image_url"]}" class="rec-image" alt="Album cover">'
    else:
        # Usar placeholder colorido
        fallback_url = get_fallback_image_url(recommendation["title"], recommendation["artist"])
        image_html = f'<img src="{fallback_url}" class="rec-image" alt="Album cover">'

    # Score de similitud
    similarity_score = recommendation.get("similarity_score", 0)
    similarity_html = f'<div class="rec-similarity">Similitud: {similarity_score:.2f}</div>'

    # Género
    genre_html = ""
    if recommendation.get('genre'):
        genre_html = f'<div class="rec-genre">{recommendation["genre"]}</div>'

    # Escapar caracteres especiales en el texto
    song_title = recommendation["title"].replace('"', '&quot;').replace("'", "&#39;")
    artist_name = recommendation["artist"].replace('"', '&quot;').replace("'", "&#39;")

    return f'<div class="rec-card">{image_html}<div class="rec-title">{song_title}</div><div class="rec-artist">por {artist_name}</div>{similarity_html}{genre_html}</div>'

def show_system_info():
    """Mostrar información sobre el sistema de recomendaciones"""
    with st.expander("🤖 ¿Cómo funciona el sistema de recomendaciones?"):
        st.markdown("""
        ### 🧠 Tecnología de IA Utilizada

        Nuestro sistema utiliza técnicas avanzadas de **procesamiento de lenguaje natural** y **machine learning**:

        **🔤 Word2Vec**: Convierte las palabras de las letras en vectores numéricos que capturan su significado semántico.

        **📊 Similitud Coseno**: Mide qué tan similares son las canciones comparando sus vectores de letras.

        **🎯 Filtrado Inteligente**: Encuentra canciones con temáticas, emociones y estilos lirícales similares.

        ### 📈 Métricas de Similitud

        - **0.8 - 1.0**: Muy similar (temática y estilo muy parecidos)
        - **0.6 - 0.8**: Similar (temática relacionada)
        - **0.4 - 0.6**: Moderadamente similar (algunos elementos en común)
        - **0.0 - 0.4**: Poco similar (diferentes temáticas)

        ### 🎵 Base de Datos

        Utiliza un dataset con miles de canciones de Spotify analizadas con sus letras completas.
        """)

def show_popular_examples():
    """Mostrar ejemplos populares para probar"""
    st.markdown("### 🔥 Prueba con Estas Canciones Populares")
    st.markdown("Haz clic en cualquier ejemplo para obtener recomendaciones instantáneas:")

    # Ejemplos organizados por género
    examples = {
        "🎤 Pop Hits": [
            ("Shape of You", "Ed Sheeran"),
            ("Blinding Lights", "The Weeknd"),
            ("Watermelon Sugar", "Harry Styles")
        ],
        "🎸 Rock Classics": [
            ("Bohemian Rhapsody", "Queen"),
            ("Sweet Child O' Mine", "Guns N' Roses"),
            ("Hotel California", "Eagles")
        ],
        "🎵 Hip Hop": [
            ("God's Plan", "Drake"),
            ("HUMBLE.", "Kendrick Lamar"),
            ("Sicko Mode", "Travis Scott")
        ]
    }

    for genre, songs in examples.items():
        st.markdown(f"**{genre}**")
        cols = st.columns(len(songs))

        for i, (song, artist) in enumerate(songs):
            with cols[i]:
                if st.button(f"{song}\n*{artist}*", key=f"example_{genre}_{i}", use_container_width=True):
                    st.session_state['example_song'] = song
                    st.session_state['example_artist'] = artist
                    st.rerun()

    # Procesar ejemplo seleccionado
    if 'example_song' in st.session_state:
        song = st.session_state['example_song']
        artist = st.session_state['example_artist']
        st.info(f"🎵 Obteniendo recomendaciones para: **{song}** por **{artist}**")
        get_and_show_recommendations(song, artist, 6)
        # Limpiar el estado
        del st.session_state['example_song']
        del st.session_state['example_artist']

def show_fallback_suggestions():
    """Mostrar sugerencias cuando no hay recomendaciones disponibles"""
    st.markdown("### 💡 Mientras tanto, puedes probar con:")

    fallback_songs = [
        "Shape of You - Ed Sheeran",
        "Blinding Lights - The Weeknd",
        "Bohemian Rhapsody - Queen",
        "God's Plan - Drake",
        "Sweet Child O' Mine - Guns N' Roses"
    ]

    for song in fallback_songs:
        st.markdown(f"• {song}")

    st.info("💡 **Tip**: Prueba con canciones populares o conocidas para mejores resultados.")
