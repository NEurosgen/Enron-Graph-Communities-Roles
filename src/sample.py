# src/sample.py
from __future__ import annotations
import random
import networkx as nx

def node_top_degree(G: nx.Graph, n_nodes: int) -> nx.Graph:
    n_nodes = min(n_nodes, G.number_of_nodes())
    deg = dict(G.degree())
    top = sorted(deg, key=deg.get, reverse=True)[:n_nodes]
    return G.subgraph(top).copy()

def node_random(G: nx.Graph, n_nodes: int, seed: int = 42) -> nx.Graph:
    n_nodes = min(n_nodes, G.number_of_nodes())
    rnd = random.Random(seed)
    nodes = list(G.nodes())
    sel = rnd.sample(nodes, n_nodes)
    return G.subgraph(sel).copy()

def random_walk(G: nx.Graph, n_nodes: int, steps: int = 50000, restarts: int = 10, seed: int = 42) -> nx.Graph:
    rnd = random.Random(seed)
    if G.number_of_nodes() <= n_nodes:
        return G.copy()
    nodes = list(G.nodes())
    current = rnd.choice(nodes)
    visited = set([current])
    for _ in range(steps):
        nbrs = list(G.neighbors(current))
        if nbrs:
            current = rnd.choice(nbrs)
        else:
            current = rnd.choice(nodes)
        visited.add(current)
        if len(visited) >= n_nodes:
            break
        # редкие рестарты
        if restarts and rnd.random() < (1.0 / max(1, steps // restarts)):
            current = rnd.choice(nodes)
    sel = list(visited)[:n_nodes]
    return G.subgraph(sel).copy()

def largest_cc(G: nx.Graph) -> nx.Graph:
    if G.is_directed():
        comp = max(nx.weakly_connected_components(G), key=len)
    else:
        comp = max(nx.connected_components(G), key=len)
    return G.subgraph(comp).copy()
