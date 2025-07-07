"""
Aplicación principal de Streamlit para el análisis de letras explícitas
Sistema ML integrado - Sin dependencia de API externa
"""

import streamlit as st
import pandas as pd
from pathlib import Path

# Configurar NLTK antes de cualquier otra importación
try:
    from utils.nltk_setup import setup_nltk_data, ensure_nltk_ready
    # Configurar NLTK al inicio de la aplicación
    setup_nltk_data()
except Exception as e:
    st.warning(f"Advertencia al configurar NLTK: {e}")

# Imports para manejo de datos y ML integrado
from utils.data_manager import DataManager

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

    # Header principal
    st.markdown('<h1 class="main-header">🎵 Explicit Lyrics Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Análisis inteligente de contenido explícito en letras de canciones</p>', unsafe_allow_html=True)

    # Sidebar para navegación
    st.sidebar.title("🔧 Navegación")
    page = st.sidebar.radio(
        "Selecciona una función:",
        ["🏠 Inicio", "🔍 Buscar Canciones", "📝 Analizar Letras", "💡 Sugerencias"]
    )

    # Estado del sistema ML (consolidado)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 Estado del Sistema")

    try:
        from utils.ml_client import get_client
        client = get_client()
        status = client.check_health()

        if hasattr(client, 'ml_available') and client.ml_available:
            if status["status"] == "healthy":
                st.sidebar.success("✅ Modelo ML: Cargado")
                st.sidebar.caption("🔧 Sistema local funcionando")
            else:
                st.sidebar.warning("⚠️ Modelo ML: No cargado")
                if st.sidebar.button("🔄 Cargar Modelo"):
                    with st.spinner("Cargando modelo..."):
                        reload_result = client.reload_model()
                        if reload_result.get("success"):
                            st.sidebar.success("Modelo cargado!")
                            st.rerun()
                        else:
                            st.sidebar.error("Error cargando modelo")
        else:
            st.sidebar.error("❌ Sistema ML no disponible")

    except Exception as e:
        st.sidebar.error("❌ Error en sistema ML")
        st.sidebar.caption(f"Detalle: {str(e)[:30]}...")

    # Estado del dataset (consolidado)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Dataset")

    try:
        data_manager = DataManager()
        df = data_manager.load_dataset()

        if not df.empty:
            from utils.cache_helpers import get_dataset_stats
            stats = get_dataset_stats(df)
            st.sidebar.info(f"📈 {stats['total_songs']:,} canciones")
            st.sidebar.info(f"🔥 {stats['explicit_count']:,} explícitas ({stats['explicit_percentage']:.1f}%)")
            st.sidebar.info(f"✅ {stats['total_songs'] - stats['explicit_count']:,} limpias")
        else:
            st.sidebar.warning("⚠️ Dataset no disponible")
            df = None

    except Exception as e:
        st.sidebar.error("❌ Error cargando dataset")
        st.sidebar.caption(f"Detalle: {str(e)[:30]}...")
        df = None

    # Navegación a páginas
    if page == "🏠 Inicio":
        show_home_page(df)
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
            st.info("Verifica que la página esté funcionando correctamente.")
    elif page == "💡 Sugerencias":
        try:
            from pages.suggestions import show_suggestions_page
            show_suggestions_page()
        except Exception as e:
            st.error(f"Error cargando página de sugerencias: {e}")
            st.info("Esta página está en desarrollo.")

def show_home_page(df: pd.DataFrame = None):
    """Página de inicio"""

    _, col2, _ = st.columns([1, 2, 1])

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
            # Usar el data_manager ya cargado
            if not df.empty:
                from utils.cache_helpers import get_dataset_stats
                stats = get_dataset_stats(df)

                col_a, col_b, col_c = st.columns(3)

                with col_a:
                    st.metric("📊 Total Canciones", f"{stats['total_songs']:,}")

                with col_b:
                    st.metric("🔥 Explícitas", f"{stats['explicit_count']:,}")

                with col_c:
                    st.metric("✅ Limpias", f"{stats['total_songs'] - stats['explicit_count']:,}")

                # Mostrar porcentaje
                st.metric("📈 Porcentaje Explícitas", f"{stats['explicit_percentage']:.1f}%")
            else:
                st.info("Dataset no disponible")

        except Exception as e:
            st.info("Cargando estadísticas del dataset...")
            st.caption(f"Debug: {str(e)}")

        st.markdown("---")
        st.markdown("### 🚀 ¡Comienza explorando!")
        st.markdown("Usa el menú de la izquierda para navegar entre las diferentes funciones.")

if __name__ == "__main__":
    main()
