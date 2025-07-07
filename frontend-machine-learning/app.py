"""
Aplicación principal de Streamlit para el análisis de letras explícitas
Sistema ML integrado - Sin dependencia de API externa
"""

import streamlit as st
import pandas as pd
from pathlib import Path

# Imports para manejo de datos y ML integrado
from utils.data_manager import DataManager
from utils.ml_status import show_ml_status_widget, require_ml_system, show_ml_info
from utils.ml_client import get_client

# Configuración de la página
st.set_page_config(
    page_title="🎵 Explicit Lyrics Analyzer",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    .explicit-word {
        background-color: #ff4444;
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: bold;
    }
    .confidence-high {
        color: #28a745;
        font-weight: bold;
    }
    .confidence-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .confidence-low {
        color: #dc3545;
        font-weight: bold;
    }
    .song-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #f8f9fa;
    }
    .song-title {
        font-size: 1.1rem;
        font-weight: bold;
        color: #333;
    }
    .song-artist {
        color: #666;
        font-style: italic;
    }
    .song-genre {
        background-color: #007bff;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        display: inline-block;
        margin-top: 0.5rem;
    }
    .explicit-badge {
        background-color: #dc3545;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .clean-badge {
        background-color: #28a745;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Función principal de la aplicación"""

    # Mostrar estado del sistema ML en la sidebar
    show_ml_status_widget()

    # Header principal
    st.markdown('<h1 class="main-header">🎵 Explicit Lyrics Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Análisis inteligente de contenido explícito en letras de canciones</p>', unsafe_allow_html=True)

    # Mostrar info del sistema ML
    show_ml_info()

    # Verificar disponibilidad del dataset
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Estado del Dataset")

    try:
        data_manager = DataManager()
        df = data_manager.load_dataset()

        if not df.empty:
            from utils.cache_helpers import get_dataset_stats
            stats = get_dataset_stats(df)
            st.sidebar.success(f"✅ Dataset: {stats['total_songs']} canciones")
            st.sidebar.info(f"🎤 {stats['artists']} artistas")
        else:
            st.sidebar.warning("⚠️ Dataset no disponible")

    except Exception:
        st.sidebar.error("❌ Error cargando dataset")

    # Sidebar para navegación
    st.sidebar.markdown("---")
    st.sidebar.title("🔧 Navegación")

    page = st.sidebar.radio(
        "Selecciona una función:",
        ["🏠 Inicio", "🔍 Buscar Canciones", "📝 Analizar Letras", "💡 Sugerencias"]
    )

    # Información de la API
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📡 Estado de la API")

    # Importar utilidades
    try:
        from utils.api_client import check_api_status
        api_status = check_api_status()
        if api_status:
            st.sidebar.success("✅ API conectada")
        else:
            st.sidebar.error("❌ API desconectada")
            st.sidebar.caption("Inicia la API con: python api.py")
    except Exception:
        st.sidebar.warning("⚠️ Verificando API...")

    # Información del dataset
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Dataset")
    try:
        from utils.data_manager import load_dataset_info
        dataset_info = load_dataset_info()
        if dataset_info['total_songs'] > 0:
            st.sidebar.info(f"📈 {dataset_info['total_songs']:,} canciones")
            st.sidebar.info(f"🔥 {dataset_info['explicit_percentage']:.1f}% explícitas")
        else:
            st.sidebar.error("❌ Dataset no cargado")
            st.sidebar.caption("Verifica que el CSV esté en data/")
    except Exception:
        st.sidebar.info("📊 Cargando información...")

    # Navegación a páginas
    if page == "🏠 Inicio":
        show_home_page()
    elif page == "🔍 Buscar Canciones":
        try:
            from pages.search_songs import show_search_page
            show_search_page()
        except Exception as e:
            st.error(f"Error cargando página de búsqueda: {e}")
            st.info("Verifica que todos los archivos estén instalados correctamente.")
    elif page == "📝 Analizar Letras":
        try:
            from pages.analyze_lyrics import show_analyze_page
            show_analyze_page()
        except Exception as e:
            st.error(f"Error cargando página de análisis: {e}")
            st.info("Verifica que la API esté funcionando correctamente.")
    elif page == "💡 Sugerencias":
        try:
            from pages.suggestions import show_suggestions_page
            show_suggestions_page()
        except Exception as e:
            st.error(f"Error cargando página de sugerencias: {e}")
            st.info("Esta página está en desarrollo.")

def show_home_page():
    """Página de inicio"""

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### 🎯 ¿Qué puedes hacer aquí?")

        st.markdown("""
        **🔍 Buscar Canciones**
        - Encuentra canciones por título o artista
        - Ve si son explícitas o no
        - Explora el contenido del dataset

        **📝 Analizar Letras**
        - Escribe tus propias letras
        - Obtén un análisis detallado
        - Ve qué palabras son consideradas explícitas

        **💡 Sugerencias**
        - Próximamente: Sistema de recomendaciones
        - Canciones similares basadas en IA
        """)

        st.markdown("---")

        # Estadísticas rápidas
        st.markdown("### 📈 Estadísticas del Dataset")

        try:
            from utils.data_manager import get_quick_stats
            stats = get_quick_stats()

            col_a, col_b, col_c = st.columns(3)

            with col_a:
                st.metric("Total Canciones", f"{stats['total']:,}")

            with col_b:
                st.metric("Canciones Explícitas", f"{stats['explicit']:,}")

            with col_c:
                st.metric("% Explícitas", f"{stats['explicit_percentage']:.1f}%")

        except Exception as e:
            st.info("Cargando estadísticas del dataset...")

        st.markdown("---")
        st.markdown("### 🚀 ¡Comienza explorando!")
        st.markdown("Usa el menú de la izquierda para navegar entre las diferentes funciones.")

if __name__ == "__main__":
    main()
