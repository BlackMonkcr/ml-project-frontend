"""
Script de prueba para verificar que todo funciona correctamente
"""

import sys
import os

# Agregar la ruta del proyecto al PYTHONPATH
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_path)

def test_dataset_loading():
    """Probar carga del dataset"""
    print("🔍 Probando carga del dataset...")

    try:
        from utils.data_manager import data_manager
        df = data_manager.load_dataset()

        if df.empty:
            print("❌ Dataset vacío o no se pudo cargar")
            return False

        print("✅ Dataset cargado correctamente")
        print(f"   Total canciones: {len(df):,}")
        print(f"   Columnas: {list(df.columns)[:5]}...")  # Mostrar primeras 5 columnas

        # Mostrar primeras 5 canciones
        print("   Primeras 5 canciones:")
        for i in range(min(5, len(df))):
            song = df.iloc[i].get('song', 'N/A')
            artist = df.iloc[i].get('Artist(s)', 'N/A')
            print(f"   {i+1}. {song} - {artist}")

        return True

        return True

    except Exception as e:
        print(f"❌ Error cargando dataset: {e}")
        return False

def test_ml_system():
    """Probar el sistema ML local"""
    print("\n🧠 Probando sistema ML local...")

    try:
        from utils.ml_functions import predict_lyrics, analyze_words

        # Datos de prueba
        test_lyrics = "This is a test song with some explicit words"

        # Probar predicción
        print("   Probando predicción...")
        result = predict_lyrics(test_lyrics, "Test Song", "Test Artist")

        if "error" in result:
            print(f"❌ Error en predicción: {result['error']}")
            return False
        else:
            print(f"✅ Predicción exitosa: {result.get('is_explicit', 'N/A')}")

        # Probar análisis de palabras
        print("   Probando análisis de palabras...")
        analysis = analyze_words(test_lyrics, "Test Song", "Test Artist")

        if "error" in analysis:
            print(f"❌ Error en análisis: {analysis['error']}")
            return False
        else:
            print(f"✅ Análisis exitoso: {len(analysis.get('explicit_words', []))} palabras encontradas")

        return True

    except Exception as e:
        print(f"❌ Error en sistema ML: {str(e)}")
        return False

def test_search_functionality():
    """Probar funcionalidad de búsqueda"""
    print("\n🔍 Probando funcionalidad de búsqueda...")

    try:
        from utils.data_manager import search_songs_paginated

        # Probar búsqueda sin filtros
        songs, total, pages = search_songs_paginated("", "", 1, 5)

        if songs:
            print(f"✅ Búsqueda sin filtros: {total:,} canciones encontradas")
            print("   Primeras 5 canciones:")
            for i, song in enumerate(songs, 1):
                print(f"   {i}. {song['title']} - {song['artist']}")
        else:
            print("❌ No se encontraron canciones")
            return False

        # Probar búsqueda específica con la primera canción
        if songs:
            test_song = songs[0]
            search_songs, search_total, _ = search_songs_paginated(
                test_song['title'], test_song['artist'], 1, 5
            )

            if search_songs:
                print(f"✅ Búsqueda específica exitosa: {search_total} resultado(s)")
            else:
                print("⚠️ Búsqueda específica no funcionó")

        return True

    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
        return False

def test_analysis_functionality():
    """Probar funcionalidad de análisis"""
    print("\n🧠 Probando funcionalidad de análisis...")

    try:
        from utils.ml_functions import predict_lyrics, analyze_words

        # Texto de prueba limpio
        clean_text = "I love you so much, you make me happy every day"
        result = predict_lyrics(clean_text)

        if "error" not in result:
            print("✅ Análisis básico funcional")
            print(f"   Texto limpio clasificado como: {'Explícito' if result.get('is_explicit') else 'Limpio'}")
            print(f"   Confianza: {result.get('confidence', 0):.3f}")
        else:
            print(f"❌ Análisis básico falló: {result['error']}")
            return False

        # Probar análisis detallado
        detailed = analyze_words(clean_text)

        if "error" not in detailed:
            print("✅ Análisis detallado funcional")
            words_count = len(detailed.get('explicit_words', []))
            print(f"   Palabras explícitas encontradas: {words_count}")
        else:
            print(f"❌ Análisis detallado falló: {detailed['error']}")

        return True

    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 EJECUTANDO PRUEBAS DEL SISTEMA")
    print("=" * 50)

    tests = [
        test_dataset_loading,
        test_ml_system,
        test_search_functionality,
        test_analysis_functionality
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 50)
    print(f"📊 RESULTADO: {passed}/{total} pruebas pasaron")

    if passed == total:
        print("🎉 ¡Todos los sistemas funcionan correctamente!")
        print("\nPuedes ejecutar la aplicación con:")
        print("streamlit run app.py")
    else:
        print("⚠️ Algunos sistemas necesitan atención:")
        if passed < 1:
            print("- Verifica que el dataset esté en data/spotify_dataset_sin_duplicados_4.csv")
        if passed < 2:
            print("- Inicia la API con: python api.py")
        if passed < 3:
            print("- Revisa la configuración del dataset")
        if passed < 4:
            print("- Verifica la conexión con la API")

if __name__ == "__main__":
    main()
