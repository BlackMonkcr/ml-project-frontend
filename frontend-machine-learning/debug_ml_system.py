#!/usr/bin/env python3
"""
Script de debug para verificar el sistema ML
"""

import sys
from pathlib import Path
import os

# Agregar el directorio current al path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

print("🔍 Depurando sistema ML...")
print(f"📁 Directorio actual: {current_dir}")

# 1. Verificar existencia del modelo
print("\n1️⃣ Verificando modelo...")
model_path = current_dir / "saved_models" / "explicit_lyrics_classifier.pkl"
print(f"📍 Ruta del modelo: {model_path}")
print(f"✅ Existe: {model_path.exists()}")
if model_path.exists():
    print(f"📊 Tamaño: {model_path.stat().st_size / 1024 / 1024:.2f} MB")

# 2. Verificar imports
print("\n2️⃣ Verificando imports...")
try:
    from utils.config import MODEL_PATH, EXPLICIT_KEYWORDS, ERROR_MESSAGES, get_model_info
    print("✅ config.py - OK")
except Exception as e:
    print(f"❌ config.py - Error: {e}")

try:
    from utils.pipeline import ModelPipeline
    print("✅ pipeline.py - OK")
except Exception as e:
    print(f"❌ pipeline.py - Error: {e}")

try:
    from utils.text_preprocessing import TextPreprocessor
    print("✅ text_preprocessing.py - OK")
except Exception as e:
    print(f"❌ text_preprocessing.py - Error: {e}")

try:
    from utils.ml_functions import (
        predict_lyrics,
        get_model_status,
        reload_model,
        ensure_model_loaded
    )
    print("✅ ml_functions.py - OK")
except Exception as e:
    print(f"❌ ml_functions.py - Error: {e}")
    import traceback
    traceback.print_exc()

try:
    from utils.ml_client import get_client
    print("✅ ml_client.py - OK")
except Exception as e:
    print(f"❌ ml_client.py - Error: {e}")

# 3. Probar la carga del cliente
print("\n3️⃣ Probando cliente ML...")
try:
    from utils.ml_client import get_client

    client = get_client()
    print(f"✅ Cliente creado: {type(client)}")
    print(f"📊 ML disponible: {getattr(client, 'ml_available', 'N/A')}")

    # Verificar estado
    status = client.check_health()
    print(f"🏥 Estado: {status}")

except Exception as e:
    print(f"❌ Error con cliente: {e}")
    import traceback
    traceback.print_exc()

# 4. Probar carga directa del modelo
print("\n4️⃣ Probando carga directa del modelo...")
try:
    from utils.ml_functions import load_ml_model

    model, success, message = load_ml_model()
    print(f"🔄 Resultado carga: {success}")
    print(f"📝 Mensaje: {message}")
    if model:
        print(f"✅ Modelo cargado: {type(model)}")

except Exception as e:
    print(f"❌ Error cargando modelo: {e}")
    import traceback
    traceback.print_exc()

# 5. Verificar dependencias
print("\n5️⃣ Verificando dependencias...")
try:
    import pickle
    print("✅ pickle - OK")
except ImportError as e:
    print(f"❌ pickle - Error: {e}")

try:
    import numpy as np
    print("✅ numpy - OK")
except ImportError as e:
    print(f"❌ numpy - Error: {e}")

try:
    import pandas as pd
    print("✅ pandas - OK")
except ImportError as e:
    print(f"❌ pandas - Error: {e}")

try:
    import sklearn
    print("✅ scikit-learn - OK")
except ImportError as e:
    print(f"❌ scikit-learn - Error: {e}")

try:
    import nltk
    print("✅ nltk - OK")
except ImportError as e:
    print(f"❌ nltk - Error: {e}")

print("\n✅ Debug completo!")
