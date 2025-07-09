import pandas as pd
import numpy as np
import re
import faiss
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import random
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from gensim.models import Word2Vec, KeyedVectors
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity
import os

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials 

# Porciacaso-------
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
Word2Vec.seed = SEED
nltk.download('punkt')
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
# Porciacaso-------




# Perdón pero hay mcuhos clases pal file y no queiro revisarlos skdjsk
DATAPATH = './data'
# LIMIT_ = 1000

@st.cache_data(show_spinner="Cargando dataset...")
def cargar_dataset(vectores_finales, LIMIT_):
    df = pd.read_csv(f"{DATAPATH}/spotify_dataset_sin_duplicados_4.csv", nrows=LIMIT_)

    df['Release Date'] = pd.to_datetime(df['Release Date'], errors='coerce')
    df['decade'] = df['Release Date'].dt.year // 10 * 10
    df['decade'] = df['decade'].fillna(0).astype(int).astype(str) + 's'

    # Clustering sobre vectores
    pca = PCA(n_components=20)
    X_reducido = pca.fit_transform(vectores_finales)
    kmeans = KMeans(n_clusters=7, random_state=SEED)
    clusters = kmeans.fit_predict(X_reducido)
    df['cluster'] = clusters
    return df

@st.cache_data(show_spinner="Cargando dataset LSH...")
def cargar_dataset_LSH():
    df = pd.read_csv(f"{DATAPATH}/spotify_dataset_sin_duplicados_4.csv")

    df['Release Date'] = pd.to_datetime(df['Release Date'], errors='coerce')
    df['decade'] = df['Release Date'].dt.year // 10 * 10
    df['decade'] = df['decade'].fillna(0).astype(int).astype(str) + 's'

    return df

@st.cache_resource(show_spinner="Cargando modelo de embeddings...")
def cargar_embeddings(LIMIT_):
    modelo = KeyedVectors.load_word2vec_format(
        f"{DATAPATH}/canciones_2_embeddings.txt",
        # os.path.join(DATAPATH, "canciones_2_embeddings.txt"),
        binary=False,
        limit=LIMIT_
    )
    return modelo

@st.cache_resource(show_spinner="Cargando vectores finales...")
def cargar_vectores_finales(_modelo_embeddings, limit):
    vectores_finales = np.array([_modelo_embeddings[f"cancion_{i}"] for i in range(limit)])
    return vectores_finales



# 🔐 Autenticación con la API de Spotify
client_id = "9d74d56ab0c5436ca827b968e647b1ca"
client_secret = "db476f73e50b473bac2fa02fe820e635"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
                                                           client_secret=client_secret))

def obtener_html_portada(song_name, album_name, artist_name, genre=None, similitud=None, release_date_dataset=None, emotion=None):
    image_url = None
    spotify_release_date = "No disponible"

    # --- Búsqueda jerárquica de imagen ---
    query = f"track:{song_name} album:{album_name} artist:{artist_name}"
    result = sp.search(q=query, type='track', limit=1)

    if result['tracks']['items']:
        track = result['tracks']['items'][0]
        image_url = track['album']['images'][0]['url']
        spotify_release_date = track['album']['release_date']
    else:
        query = f"album:{album_name} artist:{artist_name}"
        result = sp.search(q=query, type='album', limit=1)
        if result['albums']['items']:
            album = result['albums']['items'][0]
            image_url = album['images'][0]['url']
            spotify_release_date = album['release_date']
        else:
            query = f"album:{album_name}"
            result = sp.search(q=query, type='album', limit=1)
            if result['albums']['items']:
                album = result['albums']['items'][0]
                image_url = album['images'][0]['url']
                spotify_release_date = album['release_date']
            else:
                query = f"artist:{artist_name}"
                result = sp.search(q=query, type='artist', limit=1)
                if result['artists']['items']:
                    artist = result['artists']['items'][0]
                    if artist.get('images'):
                        image_url = artist['images'][0]['url']

    # --- HTML de la tarjeta ---
    if similitud is None and image_url:
        html = f"""
            <div>
            <img src="{image_url}" alt="cover"><br>
            <b>{song_name}</b>
            <small>{artist_name}</small>
            <small>{genre or ''}</small>
            <small>📅 {release_date_dataset or ''}</small>
            <small>🗓 {spotify_release_date}</small>
            </div>
            """
        return html

    if image_url:
        html = f"""
            <img src="{image_url}" alt="cover"><br>
            <b>{song_name}</b>
            <small>{artist_name}</small>
            <small>{genre or ''}</small>
            <small>📅 {release_date_dataset or ''}</small>
            <small>🗓 {spotify_release_date}</small>
            {'<small>🔗 %.2f</small>' % similitud if similitud else ''}
            {'<small>🎭 %s</small>' % emotion if emotion else ''}
        """
  
    else:
        html = f"""
            <div style="width:150px;height:150px;background:#ccc;border-radius:8px;"></div>
            <b>{song_name}</b><br>
            <small>{artist_name}</small><br>
            <small>No se encontró imagen</small>
        """


    return html


def recomendar_con_LSH(id_cancion, df_lsh, top_n=5):
    index_lsh_512 = faiss.read_index(DATAPATH+ "/faiss_LSH_512.index")
    song_ids = [f"cancion_{i}" for i in df_lsh.index]
    idx = song_ids.index(id_cancion) 
    query_vec = X[idx].reshape(1, -1).astype('float32')
    
    


def show_suggestions_page_d(df, vectores_finales, LIMIT_):
    from utils.data_manager import get_suggestions, get_song_by_title_artist, get_id_chi

    st.markdown("## 🎼 Recomendaciones basadas en letras y emociones")

    # --- CSS Carrusel ---
    st.markdown("""
        <style>
        .recs-container {
            display: flex;
            overflow-x: auto;
            gap: 16px;
            padding: 10px 0;
            scroll-behavior: smooth;
        }

        .recs-container::-webkit-scrollbar {
            height: 8px;
        }
        .recs-container::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 4px;
        }

        .rec-card {
            flex: 0 0 auto;
            width: 180px;
            background: white;
            padding: 10px;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            text-align: center;
        }

        .rec-card img {
            width: 160px;
            height: 160px;
            object-fit: cover;
            border-radius: 10px;
            margin-bottom: 8px;
        }

        .rec-card small {
            display: block;
            color: #777;
            margin-top: 4px;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Formulario ---
    with st.form("recommendation_form"):
        st.markdown("### 🔍 Buscar canciones similares")
        col1, col2 = st.columns([2, 1])
        with col1:
            song_name = st.text_input("🎤 Nombre de la canción", placeholder="Ej: Imagine")
        with col2:
            artist_name = st.text_input("🎸 Artista (opcional)", placeholder="Ej: John Lennon")

        max_recommendations = st.slider("🎯 Número de recomendaciones", 3, 12, 6)
        by_id = st.checkbox("Buscar por ID de canción", value=False)
        song_id = st.number_input("Ingresa el ID de la canción:", min_value=0, step=1)
        st.write(f"ID ingresado: {song_id}")
        submit = st.form_submit_button("🔍 Obtener recomendaciones", use_container_width=True)

    if submit and song_name.strip() or by_id == True:
        id_song = None
        if by_id:
            id_song = song_id
            if id_song>=LIMIT_:
                st.info("La canción seleccionada está fuera del límite, se eligió una canción aleatoria del dataset.")
                id_song = random.randint(0, LIMIT_ - 1)
                song_name = df.loc[song_id, 'song']
            st.info(f"Buscando recomendaciones para la canción con ID: {song_id}")
        else:
            id_song = get_id_chi(song_name.strip(), artist_name.strip())

        if id_song is not None:
            if by_id: 
                song_name = df.loc[song_id, 'song']

            if id_song >= LIMIT_:
                st.info("La canción seleccionada está fuera del límite, se eligió una canción aleatoria del dataset.")
                id_song = random.randint(0, LIMIT_ - 1)
                song_name = df.loc[id_song, 'song']

            recomendados, similitudes = recomendar_por_cluster(id_song, df, vectores_finales, top_n=max_recommendations)
            indices = recomendados.index

            base_row = df.loc[id_song]
            html_cancion_base = obtener_html_portada(
                song_name.strip(),
                base_row['Album'],
                base_row['Artist(s)'],
                base_row['Genre'],
                None,
                base_row['Release Date'],
                base_row.get('emotion', None)
            )

            st.markdown("### Canción de búsqueda:")
            # st.markdown(html_cancion_base, unsafe_allow_html=True)
            st.markdown("""
            <style>
            .base-card {
                max-width: 420px;
                background: #f8f8f8;
                padding: 10px;
                border-radius: 10px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                text-align: center;
                margin-bottom: 10px;
            }
            .base-card img {
                width: 320px;
                height: 320px;
                object-fit: cover;
                border-radius: 8px;
            }
            .base-card small {
                display: block;
                color: #666;
                margin-top: 1px;
            }
            </style>
        """, unsafe_allow_html=True)
            st.markdown(f'<div class="base-card">{html_cancion_base}</div>', unsafe_allow_html=True)

            st.markdown("### Recomendaciones similares:")
            html_carrusel = '<div class="recs-container">'
            for i, sim in zip(indices, similitudes):
                html = obtener_html_portada(
                    df.loc[i, 'song'],
                    df.loc[i, 'Album'],
                    df.loc[i, 'Artist(s)'],
                    df.loc[i, 'Genre'],
                    sim,
                    df.loc[i, 'Release Date'],
                    df.loc[i, 'emotion'],
                )
                html_carrusel += f'<div class="rec-card">{html}</div>'
            html_carrusel += '</div>'

            st.markdown(html_carrusel, unsafe_allow_html=True)


        else:
            st.error("🎵 Canción no encontrada en el dataset.")
    elif submit and by_id == False:
        st.error("Por favor, ingresa el nombre de una canción o marca la opción de búsqueda por ID.")

def recomendar_por_cluster(id_cancion, df, X_total, top_n=5):
    cluster = df.loc[id_cancion, 'cluster']
    decada = df.loc[id_cancion, 'decade']
    misma_epoca = df[(df['cluster'] == cluster) & (df['decade'] == decada)].drop(index=id_cancion)

    vectores_cluster = X_total[misma_epoca.index]
    vector_base = X_total[id_cancion].reshape(1, -1)

    similitudes = cosine_similarity(vector_base, vectores_cluster)[0]
    top_indices = similitudes.argsort()[::-1][:top_n]
    recomendados = misma_epoca.iloc[top_indices]
    scores = similitudes[top_indices]

    return recomendados, scores