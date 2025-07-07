"""
Widget de estado ML mejorado para mostrar sistema integrado vs API
"""

import streamlit as st
from typing import Dict, Any

def show_ml_status_widget():
    """Widget para mostrar el estado del sistema ML en la sidebar"""
    
    with st.sidebar:
        st.header("🤖 Estado del Sistema ML")
        
        try:
            # Importar cliente inteligente
            from .ml_client import get_client
            
            client = get_client()
            status = client.check_health()
            
            # Mostrar estado según el tipo de sistema
            if hasattr(client, 'ml_available') and client.ml_available:
                # Sistema ML integrado
                st.info("🔧 **Modo: ML Integrado**")
                
                if status["status"] == "healthy":
                    st.success("✅ Modelo ML Cargado")
                    st.caption("Sistema funcionando localmente")
                else:
                    st.warning("⚠️ Modelo ML no cargado")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🔄 Cargar Modelo"):
                            with st.spinner("Cargando modelo..."):
                                reload_result = client.reload_model()
                                if reload_result.get("success"):
                                    st.success("Modelo cargado!")
                                    st.rerun()
                                else:
                                    st.error("Error cargando modelo")
                    
                    with col2:
                        if st.button("🔍 Verificar"):
                            st.rerun()
                
            else:
                # API externa (fallback)
                st.info("🌐 **Modo: API Externa**")
                
                if status["status"] == "healthy":
                    st.success("✅ API Conectada")
                elif status["status"] == "unhealthy":
                    st.warning("⚠️ API disponible, modelo no cargado")
                else:
                    st.error("❌ API no disponible")
                    
                    # Instrucciones para API
                    with st.expander("🔧 Iniciar API"):
                        st.markdown("""
                        **Para iniciar la API:**
                        ```bash
                        cd ../ml-project-models/
                        python api.py
                        ```
                        
                        O usar el script automático:
                        ```bash
                        ./start_api.sh
                        ```
                        """)
            
            # Información adicional
            st.caption(f"🕐 {status.get('timestamp', 'N/A')}")
            
            # Botón de recarga general
            if st.button("🔄 Actualizar Estado"):
                # Limpiar cliente global para forzar re-detección
                from . import ml_client
                ml_client.smart_client = None
                st.rerun()
                
        except Exception as e:
            st.error("❌ Error en sistema ML")
            st.caption(f"Error: {str(e)}")
            
            # Modo degradado - mostrar instrucciones
            with st.expander("⚠️ Modo Degradado"):
                st.markdown("""
                **El sistema ML no está disponible.**
                
                **Opciones:**
                1. Verificar que el modelo existe en `../ml-project-models/saved_models/`
                2. Instalar dependencias: `pip install scikit-learn pandas numpy`
                3. Reiniciar la aplicación
                
                **O usar API externa:**
                ```bash
                cd ../ml-project-models/
                python api.py
                ```
                """)

def require_ml_system():
    """Verificar que el sistema ML esté disponible antes de usar funciones ML"""
    try:
        from .ml_client import get_client
        
        client = get_client()
        status = client.check_health()
        
        if status["status"] == "healthy":
            return True
        
        # Sistema disponible pero modelo no cargado
        if status["status"] in ["unhealthy"]:
            st.warning("🤖 **Sistema ML disponible pero modelo no cargado**")
            st.markdown("""
            El sistema está disponible pero necesita cargar el modelo.
            **Usa el botón "Cargar Modelo" en la sidebar** ➡️
            """)
            return False
        
        # Sistema no disponible
        st.error("🚫 **Sistema ML no disponible**")
        st.markdown("""
        Esta funcionalidad requiere el sistema ML.
        
        **Opciones:**
        1. **Verificar modelo:** Asegúrate de que el archivo del modelo existe
        2. **Instalar dependencias:** `pip install scikit-learn pandas numpy`
        3. **Usar API externa:** Ejecuta `./start_api.sh` desde el directorio principal
        """)
        
        return False
        
    except Exception as e:
        st.error(f"❌ Error verificando sistema ML: {e}")
        return False

def show_ml_info():
    """Mostrar información del sistema ML en uso"""
    try:
        from .ml_client import get_client
        
        client = get_client()
        
        if hasattr(client, 'ml_available') and client.ml_available:
            st.info("🔧 **Usando Sistema ML Integrado** - Procesamiento local, sin dependencias de API externa")
        else:
            st.info("🌐 **Usando API Externa** - Conectado a servidor ML independiente")
            
    except:
        st.warning("⚠️ **Sistema ML en modo degradado** - Funcionalidad limitada")

def get_system_info() -> Dict[str, Any]:
    """Obtener información del sistema para debugging"""
    try:
        from .ml_client import get_client
        
        client = get_client()
        status = client.check_health()
        
        return {
            "system_type": "ML Integrado" if hasattr(client, 'ml_available') and client.ml_available else "API Externa",
            "status": status["status"],
            "model_loaded": status.get("model_loaded", False),
            "available": True
        }
        
    except Exception as e:
        return {
            "system_type": "Desconocido",
            "status": "error",
            "model_loaded": False,
            "available": False,
            "error": str(e)
        }
