from cdlib import algorithms, evaluation
import networkx as nx

def detect_louvain(G: nx.Graph):
    return algorithms.louvain(G)

def detect_leiden(G: nx.Graph):
    return algorithms.leiden(G)

def modularity(G: nx.Graph, coms) -> float:
    q = evaluation.newman_girvan_modularity(G, coms).score
    return float(q)
