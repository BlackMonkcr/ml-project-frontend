"""
Script de utilidad para verificar y gestionar la conexión con la API
"""

import streamlit as st
import requests
import subprocess
import time
import threading
import os
import signal
from pathlib import Path
from typing import Optional, Dict, Any

API_URL = "http://localhost:8000"
API_PROCESS = None

class APIManager:
    """Clase para gestionar la API del backend"""

    def __init__(self, api_url: str = API_URL):
        self.api_url = api_url
        self.process = None

    def is_api_running(self) -> bool:
        """Verificar si la API está corriendo"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=3)
            return response.status_code == 200
        except:
            return False

    def get_api_status(self) -> Dict[str, Any]:
        """Obtener estado detallado de la API"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "data": response.json(),
                    "url": self.api_url
                }
            else:
                return {
                    "status": "error",
                    "message": f"API respondió con código {response.status_code}",
                    "url": self.api_url
                }
        except requests.exceptions.ConnectionError:
            return {
                "status": "offline",
                "message": "No se puede conectar con la API",
                "url": self.api_url
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error: {str(e)}",
                "url": self.api_url
            }

    def start_api_local(self) -> bool:
        """Intentar iniciar la API localmente"""
        try:
            # Buscar el script de inicio
            api_script = Path("start_api.sh")
            if not api_script.exists():
                return False

            # Iniciar proceso en background
            self.process = subprocess.Popen(
                ["bash", str(api_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )

            # Esperar un poco para que inicie
            time.sleep(5)

            # Verificar si está corriendo
            return self.is_api_running()

        except Exception as e:
            st.error(f"Error iniciando API: {e}")
            return False

    def stop_api_local(self):
        """Detener la API local"""
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.process = None
            except:
                pass

def show_api_status_widget():
    """Widget para mostrar el estado de la API en la sidebar"""
    api_manager = APIManager()

    with st.sidebar:
        st.header("🔗 Estado de la API")

        # Verificar estado
        status = api_manager.get_api_status()

        if status["status"] == "healthy":
            st.success("✅ API Conectada")
            data = status.get("data", {})
            st.info(f"🕐 {data.get('timestamp', 'N/A')}")

            if st.button("🔄 Recargar Estado", key="api_reload_status"):
                st.rerun()

        elif status["status"] == "offline":
            st.error("❌ API Desconectada")
            st.warning(status["message"])

            col1, col2 = st.columns(2)

            with col1:
                if st.button("🚀 Iniciar API", key="api_start_button"):
                    with st.spinner("Iniciando API..."):
                        if api_manager.start_api_local():
                            st.success("API iniciada!")
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("No se pudo iniciar la API automáticamente")

            with col2:
                if st.button("🔄 Verificar", key="api_verify_button"):
                    st.rerun()

            # Instrucciones manuales
            with st.expander("📋 Inicio Manual"):
                st.markdown("""
                **Para iniciar la API manualmente:**

                1. **Terminal/Consola:**
                ```bash
                cd ml-project-models/
                python -m venv venv_api
                source venv_api/bin/activate  # Linux/Mac
                # o
                venv_api\\Scripts\\activate   # Windows
                pip install -r requirements_api.txt
                uvicorn api:app --reload --host 0.0.0.0 --port 8000
                ```

                2. **Script automático:**
                ```bash
                # Linux/Mac
                cd frontend-machine-learning/
                ./start_api.sh

                # Windows
                cd frontend-machine-learning/
                start_api.bat
                ```

                3. **Verificar:**
                - API: http://localhost:8000
                - Docs: http://localhost:8000/docs
                """)

        else:
            st.warning("⚠️ API con problemas")
            st.error(status["message"])

            if st.button("🔄 Reintentar", key="api_retry_button"):
                st.rerun()

def require_api_connection():
    """Decorador/función que requiere conexión API activa"""
    api_manager = APIManager()

    if not api_manager.is_api_running():
        st.error("🚫 **API requerida pero no disponible**")
        st.markdown("""
        Esta funcionalidad requiere que la API esté corriendo.
        Por favor:

        1. **Inicia la API** usando la sidebar ➡️
        2. **O ejecuta manualmente:**
           ```bash
           cd frontend-machine-learning/
           ./start_api.sh  # Linux/Mac
           # o
           start_api.bat   # Windows
           ```
        3. **Recarga esta página** una vez que la API esté corriendo
        """)

        # Botón de recarga rápida
        if st.button("🔄 Verificar API ahora", key="api_verify_now"):
            st.rerun()

        return False

    return True

def init_api_status():
    """Inicializar el widget de estado de API"""
    if 'api_status_initialized' not in st.session_state:
        st.session_state.api_status_initialized = True
        show_api_status_widget()

# Instancia global del manager
api_manager = APIManager()
