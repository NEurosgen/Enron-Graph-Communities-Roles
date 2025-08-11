import numpy as np
import pandas as pd
import networkx as nx
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

def compute_node_features(G: nx.Graph) -> pd.DataFrame:
    deg = dict(G.degree())
    btw = nx.betweenness_centrality(G, normalized=True)
    clo = nx.closeness_centrality(G)
    pr  = nx.pagerank(G, alpha=0.85)
    cc  = nx.clustering(G)
    df = pd.DataFrame({
        "node": list(G.nodes()),
        "degree": [deg[n] for n in G.nodes()],
        "betweenness": [btw[n] for n in G.nodes()],
        "closeness": [clo[n] for n in G.nodes()],
        "pagerank": [pr[n] for n in G.nodes()],
        "clustcoef": [cc[n] for n in G.nodes()],
    })
    return df

def cluster_roles(df: pd.DataFrame, k: int | None = None, k_range=range(2,7)):
    X = df.drop(columns=["node"]).values
    Xs = StandardScaler().fit_transform(X)
    best = {"k": None, "score": -1, "labels": None, "model": None}
    if k is not None:
        model = KMeans(n_clusters=k, n_init="auto", random_state=42).fit(Xs)
        return model.labels_, model
    for kk in k_range:
        model = KMeans(n_clusters=kk, n_init="auto", random_state=42).fit(Xs)
        labels = model.labels_
        score = silhouette_score(Xs, labels)
        if score > best["score"]:
            best = {"k": kk, "score": score, "labels": labels, "model": model}
    return best["labels"], best["model"]
