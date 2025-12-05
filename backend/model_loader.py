# backend/model_loader.py
import os
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Nuevos archivos generados después de traducir + proveedores
EMB_PATH = os.path.join(DATA_DIR, "embeddings_es.npy")
INDEX_PATH = os.path.join(DATA_DIR, "faiss_index_es.bin")
META_PATH = os.path.join(DATA_DIR, "metadata_es.csv")

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"

_model = None
_index = None
_metadata = None


def load_model():
    """Carga el modelo de embeddings en español."""
    global _model
    if _model is None:
        print("Loading embedding model:", MODEL_NAME)
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def load_metadata():
    """Carga metadata en español, providers incluidos."""
    global _metadata
    if _metadata is None:
        print("Loading metadata:", META_PATH)
        _metadata = pd.read_csv(META_PATH).fillna("")
    return _metadata


def load_faiss_index():
    """Carga el índice FAISS usando los embeddings en español."""
    global _index
    if _index is None:
        print("Loading FAISS index:", INDEX_PATH)
        _index = faiss.read_index(INDEX_PATH)
    return _index
