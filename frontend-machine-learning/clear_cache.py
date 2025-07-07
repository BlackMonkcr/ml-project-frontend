"""
Script para limpiar cache de Streamlit y forzar recarga
"""

import streamlit as st
import shutil
import os
from pathlib import Path

def clear_streamlit_cache():
    """Limpiar cache de Streamlit"""
    # Ubicaciones comunes del cache de Streamlit
    cache_paths = [
        Path.home() / '.streamlit',
        Path.cwd() / '.streamlit',
        Path.home() / '.cache' / 'streamlit',
    ]

    for cache_path in cache_paths:
        if cache_path.exists():
            try:
                shutil.rmtree(cache_path)
                print(f"✅ Cache eliminado: {cache_path}")
            except Exception as e:
                print(f"❌ Error eliminando cache en {cache_path}: {e}")

    print("🔄 Cache de Streamlit limpiado")

if __name__ == "__main__":
    clear_streamlit_cache()
    print("✅ ¡Cache limpiado! Reinicia Streamlit.")
