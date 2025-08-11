from pathlib import Path
import networkx as nx

def load_enron_edge_list(path: str | Path, undirected: bool = True) -> nx.Graph:
    path = Path(path)
    G = nx.read_edgelist(path, comments="#", delimiter=None, create_using=nx.DiGraph, nodetype=str)
    if undirected:
        G = G.to_undirected()
    if isinstance(G, (nx.MultiGraph, nx.MultiDiGraph)):
        G = nx.Graph(G) if undirected else nx.DiGraph(G)
    if undirected:
        if not nx.is_connected(G):
            largest_cc = max(nx.connected_components(G), key=len)
            G = G.subgraph(largest_cc).copy()
    else:
        largest_wcc = max(nx.weakly_connected_components(G), key=len)
        G = G.subgraph(largest_wcc).copy()
    isolates = list(nx.isolates(G))
    if isolates:
        G.remove_nodes_from(isolates)
    return G
