"""
Script para reentrenar el modelo sin dependencias externas
"""

import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score
from pathlib import Path
import sys
import os

# Agregar el directorio utils al path
current_dir = Path(__file__).parent
utils_dir = current_dir / "utils"
sys.path.append(str(utils_dir))

# Importar nuestros módulos locales
from text_preprocessing import TextPreprocessor
from pipeline import ModelPipeline

def load_data():
    """Cargar el dataset de Spotify"""
    data_path = current_dir / "data" / "spotify_dataset_sin_duplicados_4.csv"

    if not data_path.exists():
        raise FileNotFoundError(f"Dataset no encontrado en {data_path}")

    df = pd.read_csv(data_path)
    print(f"Dataset cargado: {len(df)} canciones")
    return df

def prepare_data(df):
    """Preparar los datos para entrenamiento"""
    # Filtrar filas con datos faltantes
    df = df.dropna(subset=['text', 'Explicit'])

    # Preparar preprocessor
    preprocessor = TextPreprocessor()

    # Limpiar textos
    print("Preprocesando letras...")
    df['text_clean'] = df['text'].apply(preprocessor.clean_text)

    # Filtrar textos muy cortos
    df = df[df['text_clean'].str.len() > 10]

    print(f"Datos después de limpieza: {len(df)} canciones")

    X = df['text_clean'].values
    y = df['Explicit'].values

    return X, y, preprocessor

def train_model(X, y, preprocessor):
    """Entrenar el modelo"""
    print("Dividiendo datos...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Vectorizando textos...")
    vectorizer = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95
    )

    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    print("Entrenando modelo...")
    model = MultinomialNB(alpha=0.1)
    model.fit(X_train_vec, y_train)

    # Evaluar
    y_pred = model.predict(X_test_vec)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"Precisión del modelo: {accuracy:.3f}")
    print("\nReporte de clasificación:")
    print(classification_report(y_test, y_pred))

    # Crear pipeline
    pipeline = ModelPipeline(preprocessor, vectorizer, model)

    return pipeline

def save_model(pipeline, model_path):
    """Guardar el modelo entrenado"""
    # Crear directorio si no existe
    model_path.parent.mkdir(exist_ok=True)

    with open(model_path, 'wb') as f:
        pickle.dump(pipeline, f)

    print(f"Modelo guardado en: {model_path}")

def test_model(pipeline):
    """Probar el modelo entrenado"""
    print("\nProbando modelo...")

    test_cases = [
        "I love you so much, you are amazing",
        "This fucking song is shit",
        "Beautiful day with sunshine",
        "Damn this is a great song"
    ]

    for text in test_cases:
        prediction = pipeline.predict([text])[0]
        probabilities = pipeline.predict_proba([text])[0]
        confidence = max(probabilities)

        print(f"Texto: '{text}'")
        print(f"Predicción: {'Explícito' if prediction else 'Limpio'}")
        print(f"Confianza: {confidence:.3f}")
        print("-" * 50)

def main():
    """Función principal"""
    try:
        print("🔄 Reentrenando modelo local...")

        # Cargar datos
        df = load_data()

        # Preparar datos
        X, y, preprocessor = prepare_data(df)

        # Entrenar modelo
        pipeline = train_model(X, y, preprocessor)

        # Guardar modelo
        model_path = current_dir / "saved_models" / "explicit_lyrics_classifier.pkl"
        save_model(pipeline, model_path)

        # Probar modelo
        test_model(pipeline)

        print("✅ Modelo reentrenado exitosamente!")

    except Exception as e:
        print(f"❌ Error reentrenando modelo: {str(e)}")
        return False

    return True

if __name__ == "__main__":
    main()
