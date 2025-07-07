#!/bin/bash
# Streamlit Cloud initialization script
# This script handles NLTK data download for cloud deployment

echo "🚀 Iniciando configuración para Streamlit Cloud..."

# Create NLTK data directory
echo "📁 Creando directorio para datos NLTK..."
mkdir -p ~/nltk_data

# Set NLTK data path
export NLTK_DATA=~/nltk_data

# Download NLTK data using Python
echo "📥 Descargando datos NLTK necesarios..."
python3 -c "
import nltk
import ssl
from pathlib import Path

# Configure SSL for restricted environments
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Set NLTK data path
nltk_data_dir = Path.home() / 'nltk_data'
if str(nltk_data_dir) not in nltk.data.path:
    nltk.data.path.append(str(nltk_data_dir))

# Download required packages
packages = ['punkt', 'punkt_tab', 'stopwords']
for package in packages:
    try:
        print(f'Downloading {package}...')
        nltk.download(package, download_dir=str(nltk_data_dir), quiet=False)
        print(f'✓ {package} downloaded successfully')
    except Exception as e:
        print(f'⚠ Error downloading {package}: {e}')

print('🎉 NLTK setup completed!')
"

echo "✅ Configuración completada. Iniciando aplicación Streamlit..."
