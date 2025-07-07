"""
Ejemplo de uso correcto del data_manager sin warnings de cache
"""

import streamlit as st
from utils.data_manager import data_manager
from utils.cache_helpers import get_dataset_stats

def main():
    st.title("🎵 Dataset Manager - Sin Warnings")

    # Cargar dataset (sin cache warnings)
    df = data_manager.load_dataset()

    if not df.empty:
        # Obtener estadísticas (usando cache seguro)
        stats = get_dataset_stats(df)

        # Mostrar información
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Canciones", stats['total_songs'])

        with col2:
            st.metric("Canciones Explícitas", stats['explicit_count'])

        with col3:
            st.metric("% Explícitas", f"{stats['explicit_percentage']:.1f}%")

        # Mostrar sample del dataset
        with st.expander("📊 Muestra del Dataset"):
            st.dataframe(df.head())

        # Información adicional
        st.info(f"🎨 Géneros disponibles: {len(stats['genres'])}")
        st.info(f"🎤 Artistas únicos: {stats['artists']}")

    else:
        st.warning("📁 Dataset no disponible. Usa las opciones de carga.")

if __name__ == "__main__":
    main()
