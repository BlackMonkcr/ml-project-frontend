# preprocess.py
import numpy as np
import faiss
import pickle

with open("./data/canciones_2_embeddings.txt", "r", encoding="utf-8") as f:
    header = f.readline()
    n_songs, dim = map(int, header.split())
    song_ids, vectors = [], []
    for line in f:
        parts = line.strip().split()
        if len(parts) != dim + 1:
            continue
        song_ids.append(parts[0])
        vectors.append([float(x) for x in parts[1:]])

X = np.array(vectors, dtype='float32')

np.save("embeddings.npy", X)             # ahora X ocupa ~200 MB
with open("song_ids.pkl", "wb") as f:
    pickle.dump(song_ids, f)

# 3. Construye y guarda tu índice LSH
bits = 512
index = faiss.IndexLSH(dim, bits)
index.add(X)
faiss.write_index(index, "faiss_LSH_512.index")
