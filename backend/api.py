# backend/api.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import requests
import pandas as pd

from backend.model_loader import load_model, load_faiss_index, load_metadata
from backend.youtube import get_trailer_id
from backend.streaming import get_streaming_availability


pd.set_option("future.no_silent_downcasting", True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Spanish artifacts
model = load_model()
index = load_faiss_index()
metadata = load_metadata()

OMDB_KEY = "cfd4f5c2"   # tu key OMDB


class Query(BaseModel):
    q: str
    k: int = 10


# -------- Query expansion --------
def expand_query(q: str):
    syn = {
        "comedia": ["humor", "divertida"],
        "terror": ["horror", "miedo"],
        "espacio": ["astronave", "planeta", "galaxia"],
        "romance": ["amor", "pareja", "relación"],
        "robots": ["androides", "ia", "inteligencia artificial"],
        "extraterrestre": ["alien", "alienígena", "ufo"],
        "accion": ["disparos", "pelea", "lucha"],
        "misterio": ["suspenso", "enigmas"],
    }

    tokens = q.lower().split()
    extra = []

    for t in tokens:
        if t in syn:
            extra += syn[t]

    return q + " " + " ".join(extra) if extra else q


def sanitize(v):
    if v is None:
        return ""
    if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
        return ""
    return v


# ------------------- API -------------------
@app.post("/search")
def search(data: Query):
    q = data.q.strip()
    k = max(1, int(data.k))

    if not q:
        return {"results": []}

    # 1) expandir query
    q_expanded = expand_query(q)

    # 2) embedding
    emb = model.encode([q_expanded], normalize_embeddings=True)

    # 3) FAISS top-k
    D, I = index.search(emb, k)
    results_idx = I[0].tolist()

    results = (
        metadata
        .iloc[results_idx]
        .copy()
        .fillna("")
        .infer_objects(copy=False)
    )

    final_results = []

    for _, row in results.iterrows():
        r = row.to_dict()
        r = {k: sanitize(v) for k, v in r.items()}

        title_es = r.get("title_es", "")
        title_en = r.get("title", "")

        print("\n==============================")
        print("🎬 DEBUG INFO FOR MOVIE")
        print("==============================")
        print("Título ES:", title_es)
        print("Título EN:", title_en)

        # ---------------- POSTER ----------------
        poster = None

        # Search poster by Spanish title
        if title_es:
            url = f"http://www.omdbapi.com/?t={title_es}&apikey={OMDB_KEY}"
            omdb = requests.get(url).json()
            print("OMDB ES response:", omdb)
            poster = omdb.get("Poster")

        # Fallback English title
        if not poster and title_en:
            url = f"http://www.omdbapi.com/?t={title_en}&apikey={OMDB_KEY}"
            omdb = requests.get(url).json()
            print("OMDB EN response:", omdb)
            poster = omdb.get("Poster")

        print("Poster final:", poster)
        r["poster"] = poster

        # ---------------- TRAILER ----------------
        trailer = get_trailer_id(title_es) or get_trailer_id(title_en)
        print("Trailer ID:", trailer)
        r["trailer_id"] = trailer

        # ---------------- STREAMING ----------------
        platforms = get_streaming_availability(title_es, title_en)
        print("Plataformas encontradas:", platforms)
        r["watch_on"] = platforms

        print("=====================================\n")

        final_results.append(r)

    return {"results": final_results}


@app.get("/")
def root():
    return {"message": "Semantic Search ES API running"}
