"""
Script de prueba para verificar el modelo con paths locales
"""

import sys
sys.path.append('.')

def test_model_loading():
    """Probar la carga del modelo con paths locales"""

    print("🧪 Probando sistema ML con paths locales...")

    try:
        # Test 1: Configuración
        from utils.config import get_model_info
        info = get_model_info()
        print("✅ Configuración cargada:")
        for key, value in info.items():
            print(f"   {key}: {value}")

        # Test 2: Funciones ML
        from utils.ml_functions import load_ml_model, get_model_path

        model_path = get_model_path()
        print(f"\n✅ Path del modelo: {model_path}")
        print(f"   Existe: {model_path.exists()}")

        # Test 3: Carga del modelo
        model, success, message = load_ml_model()
        print(f"\n📦 Carga del modelo:")
        print(f"   Éxito: {success}")
        print(f"   Mensaje: {message}")

        if success and model:
            # Test 4: Predicción simple
            print(f"\n🎯 Prueba de predicción...")

            # Datos de prueba
            test_cases = [
                "This is a clean song about love and happiness",
                "This song contains some bad fucking words and shit",
                "Just a normal song with regular lyrics"
            ]

            for i, lyrics in enumerate(test_cases, 1):
                try:
                    prediction = model.predict([lyrics])
                    probabilities = model.predict_proba([lyrics])

                    is_explicit = bool(prediction[0])
                    confidence = float(max(probabilities[0]))

                    print(f"   Test {i}: {'Explícito' if is_explicit else 'Limpio'} ({confidence:.2f})")

                except Exception as e:
                    print(f"   Test {i}: Error - {e}")

            print("\n🎉 Todos los tests completados exitosamente!")
            return True

        else:
            print(f"\n❌ No se pudo cargar el modelo: {message}")
            return False

    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

if __name__ == "__main__":
    success = test_model_loading()
    sys.exit(0 if success else 1)
