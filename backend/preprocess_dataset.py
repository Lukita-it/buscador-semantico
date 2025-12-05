# backend/add_providers_and_build_index.py

import os
import json
import time
from tqdm import tqdm
import requests
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Archivos de entrada
META_ES_PATH = os.path.join(DATA_DIR, "metadata_es.csv")
RAW_CSV_PATH = os.path.join(DATA_DIR, "imdb_movie_dataset.csv")

# Archivos de salida
OUT_META = os.path.join(DATA_DIR, "metadata_es.csv")
OUT_PROV_CACHE = os.path.join(DATA_DIR, "providers_cache.json")
OUT_EMB = os.path.join(DATA_DIR, "embeddings_es.npy")
OUT_FAISS = os.path.join(DATA_DIR, "faiss_index_es.bin")

# ---------------------------
# TMDB API KEY (PEDIDA)
# ---------------------------
TMDB_API_KEY = "026cab7367a257c7d8aaec6a5f184f33"   # <- CAMBIAR
TMDB_COUNTRY = "PE"

# Modelo de embeddings
EMB_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
BATCH_SIZE = 64
SLEEP_BETWEEN_REQUESTS = 0.25


# ------------------------------------------------------------------
# funciones TMDB
# ------------------------------------------------------------------
def tmdb_search_movie(title, year=None):
    """Busca la película en TMDB y devuelve dict o None."""
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": title,
        "language": "en-US"
    }
    if year and str(year).isdigit():
        params["year"] = int(year)

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        results = r.json().get("results", [])
        return results[0] if results else None
    except:
        return None


def tmdb_get_providers(movie_id):
    """Obtiene proveedores (Netflix, Prime, etc) desde TMDB."""
    if not movie_id:
        return []

    url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers"
    params = {"api_key": TMDB_API_KEY}

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json().get("results", {})
        region = data.get(TMDB_COUNTRY)
        if not region:
            return []

        flatrate = region.get("flatrate", []) or []
        providers = [p["provider_name"] for p in flatrate if "provider_name" in p]
        return list(dict.fromkeys(providers))  # quitar duplicados
    except:
        return []


# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------
def main():
    if TMDB_API_KEY == "" or TMDB_API_KEY == "AQUI_TU_API_KEY":
        print("⚠ ERROR: Configura tu TMDB_API_KEY dentro del archivo.")
        return

    # ------------------------------------------------------------------
    # 1. Cargar dataset
    # ------------------------------------------------------------------
    if os.path.exists(META_ES_PATH):
        print("Cargando metadata_es.csv...")
        df = pd.read_csv(META_ES_PATH).fillna("")
    else:
        print("No existe metadata_es.csv. Cargando CSV original...")
        df = pd.read_csv(RAW_CSV_PATH).fillna("")

        # Normalizar columnas
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        # Crear columnas en español si no existen
        if "title_es" not in df.columns:
            df["title_es"] = df["title"]
        if "genre_es" not in df.columns:
            df["genre_es"] = df["genre"]
        if "description_es" not in df.columns:
            df["description_es"] = df["description"]

    n = len(df)
    print(f"Películas cargadas: {n}")

    # ------------------------------------------------------------------
    # 2. Cargar cache de proveedores
    # ------------------------------------------------------------------
    if os.path.exists(OUT_PROV_CACHE):
        with open(OUT_PROV_CACHE, "r", encoding="utf-8") as f:
            prov_cache = json.load(f)
    else:
        prov_cache = {}

    providers_col = []

    print("Buscando proveedores reales en TMDB...")
    for idx, row in tqdm(df.iterrows(), total=n):
        title = row.get("title", "")
        year = row.get("year", "")

        cache_key = f"{title}|{year}"

        if cache_key in prov_cache:
            providers = prov_cache[cache_key]
        else:
            result = tmdb_search_movie(title, year)
            movie_id = result["id"] if result else None
            plist = tmdb_get_providers(movie_id)
            providers = ", ".join(plist) if plist else "No disponible"

            prov_cache[cache_key] = providers

            with open(OUT_PROV_CACHE, "w", encoding="utf-8") as f:
                json.dump(prov_cache, f, ensure_ascii=False, indent=2)

            time.sleep(SLEEP_BETWEEN_REQUESTS)

        providers_col.append(providers)

    df["providers"] = providers_col

    # ------------------------------------------------------------------
    # 3. Crear campo text_es para embeddings
    # ------------------------------------------------------------------
    texts = []
    for _, r in df.iterrows():
        txt = (
            f"{r['title_es']}. "
            f"{r['genre_es']}. "
            f"{r['description_es']}. "
            f"Disponible en: {r['providers']}"
        )
        texts.append(txt)

    df["text_es"] = texts

    # Guardar metadata final
    df.to_csv(OUT_META, index=False, encoding="utf-8")
    print("Metadata final guardada en:", OUT_META)

    # ------------------------------------------------------------------
    # 4. Generar embeddings
    # ------------------------------------------------------------------
    print("Cargando modelo de embeddings:", EMB_MODEL_NAME)
    model = SentenceTransformer(EMB_MODEL_NAME)

    print("Generando embeddings...")
    emb = model.encode(
        df["text_es"].tolist(),
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    emb = np.array(emb, dtype="float32")
    np.save(OUT_EMB, emb)
    print("Embeddings guardados en:", OUT_EMB)

    # ------------------------------------------------------------------
    # 5. Crear FAISS
    # ------------------------------------------------------------------
    dim = emb.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(emb)
    faiss.write_index(index, OUT_FAISS)
    print("FAISS guardado en:", OUT_FAISS)

    print("\n🎉 PROCESO COMPLETO\n")


if __name__ == "__main__":
    main()
