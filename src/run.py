import argparse
from pathlib import Path
import networkx as nx  

from src.datasets import load_enron_edge_list
from src.communities import detect_louvain, detect_leiden, modularity
from src.roles import compute_node_features, cluster_roles
from src.viz import draw_communities_roles
from src.sample import node_top_degree, node_random, random_walk, largest_cc


def main():
    p = argparse.ArgumentParser()

    p.add_argument("--data", default="data/email-enron.txt")
    p.add_argument("--algo", choices=["louvain", "leiden"], default="louvain")
    p.add_argument("--k", type=int, default=None, help="k для k-means ролей (если None — авто)")
    p.add_argument("--outdir", default="results")


    p.add_argument("--sample", choices=["none", "topdeg", "random", "rw"], default="none",
                   help="метод сэмплинга подграфа")
    p.add_argument("--sample-size", type=int, default=5000,
                   help="сколько узлов оставить в подграфе")
    p.add_argument("--seed", type=int, default=42)

    p.add_argument("--no-betw", action="store_true",
                   help="не считать betweenness (ускоряет сильно)")
    p.add_argument("--betw-k", type=int, default=256,
                   help="кол-во источников для аппроксимации betweenness")

    p.add_argument("--plot-n", type=int, default=2000,
                   help="сколько узлов рисовать (top по степени)")

    args = p.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    G = load_enron_edge_list(args.data, undirected=True)

    if args.sample != "none":
        print(f"[INFO] sampling method={args.sample} size={args.sample_size} seed={args.seed}")
        if args.sample == "topdeg":
            G = node_top_degree(G, args.sample_size)
        elif args.sample == "random":
            G = node_random(G, args.sample_size, seed=args.seed)
        elif args.sample == "rw":
            G = random_walk(G, args.sample_size,
                            steps=args.sample_size * 10, restarts=10, seed=args.seed)
            if G.number_of_nodes() > 0 and not nx.is_connected(G):
                G = largest_cc(G)
        print(f"[INFO] sampled graph: |V|={G.number_of_nodes()} |E|={G.number_of_edges()}")

    if args.algo == "louvain":
        coms = detect_louvain(G)
    else:
        coms = detect_leiden(G)
    q = modularity(G, coms)
    print(f"[INFO] communities: {len(coms.communities)} | modularity Q={q:.4f}")

    try:
        df_feat = compute_node_features(G, approx_betw=(not args.no_betw), betw_k=args.betw_k)
    except TypeError:
        df_feat = compute_node_features(G)

    labels, model = cluster_roles(df_feat, k=args.k)
    df_feat["role"] = labels
    df_feat.to_csv(outdir / "node_roles.csv", index=False)
    print(f"[INFO] roles: k={len(set(labels))}")

    png_path = outdir / f"enron_{args.algo}_roles.png"
    try:
        draw_communities_roles(G, coms, labels, outpath=png_path, plot_n=args.plot_n)
    except TypeError:
        draw_communities_roles(G, coms, labels, outpath=png_path)
    print(f"[INFO] saved plot -> {png_path}")


if __name__ == "__main__":
    main()
