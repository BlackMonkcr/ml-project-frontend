#!/usr/bin/env python3
"""
Script de verificación rápida para las páginas de Streamlit
"""

import sys
from pathlib import Path

# Agregar el directorio current al path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

print("🔍 Verificando páginas de Streamlit...")

# 1. Verificar import de páginas
print("\n1️⃣ Verificando imports de páginas...")
try:
    from pages.search_songs import show_search_page
    print("✅ search_songs.py - OK")
except Exception as e:
    print(f"❌ search_songs.py - Error: {e}")

try:
    from pages.analyze_lyrics import show_analyze_page
    print("✅ analyze_lyrics.py - OK")
except Exception as e:
    print(f"❌ analyze_lyrics.py - Error: {e}")

try:
    from pages.suggestions import show_suggestions_page
    print("✅ suggestions.py - OK")
except Exception as e:
    print(f"❌ suggestions.py - Error: {e}")

# 2. Verificar utilidades principales
print("\n2️⃣ Verificando utilidades...")
try:
    from utils.data_manager import DataManager
    dm = DataManager()
    print("✅ DataManager - OK")
except Exception as e:
    print(f"❌ DataManager - Error: {e}")

try:
    from utils.ml_client import get_client
    client = get_client()
    print("✅ ML Client - OK")
except Exception as e:
    print(f"❌ ML Client - Error: {e}")

print("\n✅ Verificación completa!")
