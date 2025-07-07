"""
Prueba rápida del sistema ML integrado
"""

import streamlit as st

def test_ml_integration():
    """Probar el sistema ML integrado"""

    st.title("🧪 Prueba del Sistema ML Integrado")

    try:
        # Test 1: Importaciones
        from utils.ml_functions import get_model_status
        from utils.ml_client import get_client
        from utils.ml_status import show_ml_status_widget

        st.success("✅ **Paso 1:** Importaciones exitosas")

        # Test 2: Estado del sistema
        try:
            client = get_client()
            status = client.check_health()

            st.info(f"**Paso 2:** Sistema ML - Estado: {status['status']}")

            if status['status'] == 'healthy':
                st.success("✅ **Paso 3:** Sistema ML listo para usar")

                # Test 3: Predicción simple
                test_lyrics = "This is a test song with clean lyrics"
                result = client.predict_lyrics(test_lyrics)

                if result and "error" not in result:
                    st.success("✅ **Paso 4:** Predicción exitosa")
                    st.json(result)
                else:
                    st.warning("⚠️ **Paso 4:** Predicción con errores")
                    st.json(result)

            else:
                st.warning("⚠️ **Paso 3:** Sistema disponible pero modelo no cargado")

        except Exception as e:
            st.error(f"❌ **Paso 2-3:** Error en sistema ML: {e}")

        # Mostrar widget de estado
        st.markdown("---")
        st.markdown("### Widget de Estado:")
        show_ml_status_widget()

    except ImportError as e:
        st.error(f"❌ **Paso 1:** Error de importación: {e}")
        st.markdown("""
        **Soluciones posibles:**
        1. Verificar que todos los archivos ML estén creados
        2. Instalar dependencias: `pip install scikit-learn pandas numpy`
        3. Verificar que el modelo existe en la ruta correcta
        """)

    except Exception as e:
        st.error(f"❌ Error general: {e}")

if __name__ == "__main__":
    test_ml_integration()
