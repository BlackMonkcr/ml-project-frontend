"""
Script para debug de la columna Explicit
"""

import pandas as pd
from pathlib import Path

# Cargar dataset
data_path = "data/spotify_dataset_sin_duplicados_4.csv"
df = pd.read_csv(data_path)

print("=== DEBUG COLUMNA EXPLICIT ===")
print(f"Total filas: {len(df)}")
print(f"Columnas disponibles: {list(df.columns)}")

if 'Explicit' in df.columns:
    print(f"\nValores únicos en 'Explicit': {df['Explicit'].value_counts()}")
    print(f"Tipo de datos: {df['Explicit'].dtype}")
    print(f"Valores nulos: {df['Explicit'].isnull().sum()}")

    # Verificar algunos ejemplos
    print(f"\nPrimeros 10 valores:")
    print(df['Explicit'].head(10).tolist())

    # Conversión a booleano
    df['is_explicit'] = df['Explicit'].str.lower() == 'yes'
    print(f"\nDespués de conversión:")
    print(df['is_explicit'].value_counts())

    # Verificar que la conversión funciona
    explicit_count = df['is_explicit'].sum()
    total_count = len(df)
    print(f"\nResumen:")
    print(f"Total canciones: {total_count}")
    print(f"Explícitas: {explicit_count}")
    print(f"Limpias: {total_count - explicit_count}")
    print(f"Porcentaje explícitas: {(explicit_count/total_count)*100:.2f}%")

else:
    print("❌ Columna 'Explicit' no encontrada!")
