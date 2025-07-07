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
        from utils.data_manager import debug_dataset_info
        info = debug_dataset_info()
        
        if "error" in info:
            print(f"❌ Error: {info['error']}")
            return False
        
        print(f"✅ Dataset cargado correctamente")
        print(f"   Total canciones: {info['total_rows']:,}")
        print(f"   Columnas: {info['columns']}")
        print(f"   Primeras 5 canciones:")
        for i, title in enumerate(info['sample_titles'][:5], 1):
            print(f"   {i}. {title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error cargando dataset: {e}")
        return False

def test_api_connection():
    """Probar conexión con la API"""
    print("\n🔗 Probando conexión con la API...")
    
    try:
        from utils.api_client import check_api_status
        status = check_api_status()
        
        if status:
            print("✅ API conectada correctamente")
            return True
        else:
            print("❌ API no disponible")
            print("   Asegúrate de que la API esté corriendo en http://localhost:8000")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando con la API: {e}")
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
        from utils.api_client import predict_lyrics_safe, analyze_words_safe
        
        # Texto de prueba limpio
        clean_text = "I love you so much, you make me happy every day"
        result = predict_lyrics_safe(clean_text)
        
        if result:
            print(f"✅ Análisis básico funcional")
            print(f"   Texto limpio clasificado como: {'Explícito' if result['is_explicit'] else 'Limpio'}")
            print(f"   Confianza: {result['confidence']:.3f}")
        else:
            print("❌ Análisis básico falló")
            return False
        
        # Probar análisis detallado
        detailed = analyze_words_safe(clean_text)
        
        if detailed:
            print("✅ Análisis detallado funcional")
            words_count = len(detailed.get('words', []))
            print(f"   Palabras analizadas: {words_count}")
        else:
            print("❌ Análisis detallado falló")
        
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
        test_api_connection,
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
