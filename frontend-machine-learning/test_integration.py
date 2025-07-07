"""
Script de prueba rápida para verificar que todo funciona sin API
"""

def test_ml_functions():
    """Probar las funciones ML locales"""
    print("🧪 Probando funciones ML locales...")

    try:
        from utils.ml_functions import predict_lyrics, analyze_words

        test_text = "I love this beautiful song so much"

        # Probar predicción
        result = predict_lyrics(test_text)
        print(f"Predicción: {result}")

        # Probar análisis
        analysis = analyze_words(test_text)
        print(f"Análisis: {analysis}")

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_data_manager():
    """Probar el data manager"""
    print("🗃️ Probando data manager...")

    try:
        from utils.data_manager import data_manager

        df = data_manager.get_dataset()
        print(f"Dataset cargado: {len(df)} filas")
        print(f"Columnas disponibles: {list(df.columns)[:5]}...")

        # Probar búsqueda
        songs, total = data_manager.search_songs("love", "", 1, 5)
        print(f"Búsqueda 'love': {len(songs)} resultados de {total}")

        if songs:
            print(f"Primera canción: {songs[0]['title']} - {songs[0]['artist']}")

        return True
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ml_status():
    """Probar el widget de estado ML"""
    print("📊 Probando widget de estado ML...")

    try:
        from utils.ml_status import show_ml_status
        # Solo verificar que se puede importar
        print("✅ Widget de estado ML importado correctamente")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Ejecutando pruebas de integración...")

    tests = [
        ("ML Functions", test_ml_functions),
        ("Data Manager", test_data_manager),
        ("ML Status", test_ml_status)
    ]

    passed = 0
    for name, test_func in tests:
        print(f"\n=== {name} ===")
        if test_func():
            print(f"✅ {name} - PASSED")
            passed += 1
        else:
            print(f"❌ {name} - FAILED")

    print(f"\n📈 Resultado: {passed}/{len(tests)} pruebas pasaron")

    if passed == len(tests):
        print("🎉 ¡Todo funciona correctamente!")
    else:
        print("⚠️ Algunas pruebas fallaron")
