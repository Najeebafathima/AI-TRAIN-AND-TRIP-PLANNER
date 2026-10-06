import os
import numpy as np
import pandas as pd
import ollama

df = pd.read_csv("data/places.csv")
CACHE = "data/embeddings.npy"

def embed(text):
    return ollama.embed(model="nomic-embed-text", input=text)["embeddings"][0]

def make_text(r):
    return f"{r['name']} in {r['city']}. {r['description']}. Best season: {r['best_season']}."

def load_vectors():
    if os.path.exists(CACHE):
        vecs = np.load(CACHE)
        if len(vecs) == len(df):
            return vecs
    vecs = np.array([embed(make_text(r)) for _, r in df.iterrows()])
    vecs = vecs / np.linalg.norm(vecs, axis=1, keepdims=True)
    np.save(CACHE, vecs)
    return vecs

VECS = load_vectors()

def search_places(query: str, city: str = "", n: int = 5):
    """Find tourist places matching a query, optionally within a city."""
    q = np.array(embed(query))
    q = q / np.linalg.norm(q)
    scores = VECS @ q
    if city:
        mask = df["city"].str.lower().eq(city.lower()).to_numpy()
        scores = np.where(mask, scores, -1)
    top = np.argsort(scores)[::-1][:n]
    return [make_text(df.iloc[i]) for i in top if scores[i] > -1]

if __name__ == "__main__":
        print(search_places("beach and nightlife", "Goa"))