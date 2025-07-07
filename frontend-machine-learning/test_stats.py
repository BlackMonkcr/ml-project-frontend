"""
Test directo de las funciones de estadísticas
"""

import sys
from pathlib import Path

# Agregar utils al path
current_dir = Path(__file__).parent
utils_dir = current_dir / "utils"
sys.path.append(str(utils_dir))

from cache_helpers import cached_load_dataset, get_dataset_stats

def test_stats():
    """Probar las estadísticas directamente"""
    print("=== TEST ESTADÍSTICAS ===")

    # Cargar dataset
    dataset_path = "data/spotify_dataset_sin_duplicados_4.csv"
    df, message, success = cached_load_dataset(dataset_path)

    print(f"Carga exitosa: {success}")
    print(f"Mensaje: {message}")
    print(f"Filas en dataframe: {len(df)}")

    if success and not df.empty:
        print(f"\nColumnas en dataframe: {list(df.columns)}")

        if 'is_explicit' in df.columns:
            print(f"Valor counts de is_explicit:")
            print(df['is_explicit'].value_counts())

        # Obtener estadísticas
        stats = get_dataset_stats(df)
        print(f"\nEstadísticas calculadas:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    else:
        print("❌ Error cargando dataset")

if __name__ == "__main__":
    test_stats()
