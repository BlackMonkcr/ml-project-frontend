"""
Script para verificar el estado de la aplicación
"""

import sys
from pathlib import Path
import streamlit as st

# Agregar utils al path
current_dir = Path(__file__).parent
utils_dir = current_dir / "utils"
sys.path.append(str(utils_dir))

from data_manager import DataManager

def test_app_stats():
    """Probar las estadísticas en el contexto de la aplicación"""
    print("=== TEST APP ESTADÍSTICAS ===")

    # Usar el mismo DataManager que usa la app
    data_manager = DataManager()
    df = data_manager.load_dataset()

    print(f"Dataset cargado: {len(df)} filas")
    print(f"Columnas disponibles: {list(df.columns)}")

    if 'is_explicit' in df.columns:
        explicit_count = df['is_explicit'].sum()
        clean_count = len(df) - explicit_count

        print(f"\nEstadísticas:")
        print(f"Total: {len(df)}")
        print(f"Explícitas: {explicit_count}")
        print(f"Limpias: {clean_count}")
        print(f"Porcentaje explícitas: {(explicit_count/len(df))*100:.2f}%")

        print(f"\nValor counts de is_explicit:")
        print(df['is_explicit'].value_counts())
    else:
        print("❌ Columna 'is_explicit' no encontrada en el DataFrame")

    # Verificar las funciones de estadísticas
    from cache_helpers import get_dataset_stats
    stats = get_dataset_stats(df)
    print(f"\nEstadísticas via cache_helpers:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    test_app_stats()
