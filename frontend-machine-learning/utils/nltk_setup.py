"""
Configuración centralizada de NLTK para Streamlit Cloud
"""

import nltk
import ssl
import os
from pathlib import Path


def setup_nltk_data():
    """
    Configurar y descargar datos necesarios de NLTK para Streamlit Cloud
    """
    # Configurar SSL para descargas en entornos restringidos
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    # Lista de paquetes NLTK necesarios
    required_packages = [
        ('punkt', 'tokenizers/punkt'),
        ('punkt_tab', 'tokenizers/punkt_tab'),
        ('stopwords', 'corpora/stopwords'),
    ]

    # Configurar directorio de datos NLTK para Streamlit Cloud
    nltk_data_dir = Path.home() / 'nltk_data'
    if not nltk_data_dir.exists():
        nltk_data_dir.mkdir(parents=True, exist_ok=True)

    # Añadir directorio a la lista de rutas de NLTK
    if str(nltk_data_dir) not in nltk.data.path:
        nltk.data.path.append(str(nltk_data_dir))

    # Descargar paquetes necesarios
    for package_name, data_path in required_packages:
        try:
            # Verificar si el paquete ya existe
            nltk.data.find(data_path)
            print(f"✓ {package_name} ya está disponible")
        except LookupError:
            try:
                print(f"Descargando {package_name}...")
                nltk.download(package_name, download_dir=str(nltk_data_dir), quiet=True)
                print(f"✓ {package_name} descargado exitosamente")
            except Exception as e:
                print(f"⚠ Error descargando {package_name}: {e}")
                # Intentar descarga alternativa
                try:
                    nltk.download(package_name, quiet=True)
                    print(f"✓ {package_name} descargado con método alternativo")
                except Exception as e2:
                    print(f"✗ No se pudo descargar {package_name}: {e2}")


def ensure_nltk_ready():
    """
    Función para asegurar que NLTK esté listo antes de usarlo
    """
    try:
        # Verificar que los tokenizadores principales estén disponibles
        from nltk.tokenize import word_tokenize
        from nltk.corpus import stopwords

        # Probar tokenización básica
        test_text = "Hello world"
        tokens = word_tokenize(test_text)

        # Probar stopwords
        stop_words = stopwords.words('english')

        return True
    except Exception as e:
        print(f"NLTK no está completamente configurado: {e}")
        # Intentar configurar de nuevo
        setup_nltk_data()
        try:
            from nltk.tokenize import word_tokenize
            tokens = word_tokenize("test")
            return True
        except:
            return False


# Ejecutar configuración al importar el módulo
if __name__ == "__main__":
    setup_nltk_data()
else:
    # Auto-configuración al importar
    setup_nltk_data()
