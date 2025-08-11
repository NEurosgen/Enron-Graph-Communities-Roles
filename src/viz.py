import matplotlib.pyplot as plt
import networkx as nx

def draw_communities_roles(G, communities, roles_labels, node_size_attr="degree", outpath=None):
    part = {}
    for cid, comm in enumerate(communities.communities):
        for n in comm:
            part[n] = cid
    deg = dict(G.degree())
    sizes = [max(50, deg[n]*2) for n in G.nodes()]
    colors = [part.get(n, -1) for n in G.nodes()]  
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(10,10))
    nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color=colors, cmap="tab20")
    nx.draw_networkx_edges(G, pos, alpha=0.2, width=0.5)
    top_nodes = sorted(deg, key=deg.get, reverse=True)[:20]
    nx.draw_networkx_labels(G, pos, labels={n:n for n in top_nodes}, font_size=1)
    plt.axis("off")
    if outpath:
        plt.savefig(outpath, dpi=200, bbox_inches="tight")
    else:
        plt.show()
