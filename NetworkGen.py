import os
import math
import random
from tqdm import tqdm
import networkx as nx
import matplotlib.pyplot as plt
#%%
def hierarchical_network (nNodesPerLevel: list[int], seed: int = 42) -> nx.DiGraph:

    assert nNodesPerLevel[-1] == 1, "Last level must have only one sink node"

    random.seed(seed)

    G = nx.DiGraph()  # Create a directed graph

    current_node = 0
    levels = {}
    nodesPerLevel = {0: 1}
    for i, n in enumerate(nNodesPerLevel, start=1):
        nodesPerLevel[i] = n

    # Add nodes at each level
    for i, n in nodesPerLevel.items():
        level_nodes = list(range(current_node, current_node + n))
        if i != 0 and i != len(nNodesPerLevel):
            levels[i] = level_nodes
        G.add_nodes_from(level_nodes, subset=i) # Assign subset attribute
        current_node += n

    # Add edges between source node and the first level
    for node in levels[1]:
        G.add_edge(0, node)

    # Add edges between intermediate nodes
    for i, level in levels.items():
        if i+1 == len(nNodesPerLevel): # Skip the last i+1 level
            break
        else:
            min_edges = max(nodesPerLevel[i], nodesPerLevel[i+1]) # Minimum of number of edges between level i and level i+1
            additional_edges = random.uniform(0.01, 0.05) * min_edges # Random number of additional edges between 1% and 5% of the minimum number of edges
            nEdges = min_edges + math.floor(additional_edges)
            # Add dummy nodes at each levels i and i+1 to match the number of required edges
            p1 = level # Nodes at level i
            p2 = levels[i+1] # Nodes at level i+1
            while len(p1) < nEdges:
                p1 += p1[:nEdges-len(p1)]
            while len(p2) < nEdges:
                p2 += p2[:nEdges-len(p2)]
            # Randomly shuffle the nodes at each level to create the required number edges
            while len(set(zip(p1, p2))) < nEdges:
                random.shuffle(p1)
                random.shuffle(p2)
            # Add edges between nodes at level i and level i+1
            for u,v in zip(p1, p2):
                G.add_edge(u,v)

    # Add edges between last level and sink node
    for node in levels[len(nNodesPerLevel)-1]:
        G.add_edge(node, current_node-1)

    return G

def non_hierarchical_network (nNodesPerLevel: list[int], seed: int = 42) -> nx.DiGraph:

    assert nNodesPerLevel[-1] == 1, "Last level must have only one sink node"

    random.seed(seed)

    G = nx.DiGraph()  # Create a directed graph

    current_node = 0
    levels = {}
    nodesPerLevel = {0: 1}
    for i, n in enumerate(nNodesPerLevel, start=1):
        nodesPerLevel[i] = n

    # Add nodes at each level
    for i, n in nodesPerLevel.items():
        level_nodes = list(range(current_node, current_node + n))
        if i != 0 and i != len(nNodesPerLevel):
            levels[i] = level_nodes
        G.add_nodes_from(level_nodes, subset=i) # Assign subset attribute
        current_node += n

    # Subset of nodes at each level to break the network into non-hierarchical structure
    levels_bar = {}
    for i, level in levels.items():
        k = random.uniform(0.01, 0.05) # Random fraction of nodes to be included in the subset between 1% and 5%
        n = math.ceil(k * len(level))
        levels_bar[i] = random.sample(level, n)

    # Add edges between source node and the first level
    for node in levels[1]:
        G.add_edge(0, node)

    # Add edges between intermediate nodes
    # Non-hierarchical structure
    for i, level in levels.items():
        if i+2 == len(nNodesPerLevel): # Skip the last i+2 level
            break
        else:
            for node in levels_bar[i]:
                k = random.randint(1, len(levels_bar[i+2])) # Random number of edges between node and other nodes at level i+2
                other_nodes = random.sample(levels_bar[i+2], k)
                for other_node in other_nodes:
                    G.add_edge(node, other_node)

    # Hierarchical structure
    for i, level in levels.items():
        if i+1 == len(nNodesPerLevel): # Skip the last i+1 level
            break
        else:
            min_edges = max(nodesPerLevel[i], nodesPerLevel[i+1]) # Minimum of number of edges between level i and level i+1
            nEdges = min_edges
            # Add dummy nodes at each levels i and i+1 to match the number of required edges
            p1 = level # Nodes at level i
            p2 = levels[i+1] # Nodes at level i+1
            while len(p1) < nEdges:
                p1 += p1[:nEdges-len(p1)]
            while len(p2) < nEdges:
                p2 += p2[:nEdges-len(p2)]
            # Randomly shuffle the nodes at each level to create the required number edges
            while len(set(zip(p1, p2))) < nEdges:
                random.shuffle(p1)
                random.shuffle(p2)
            # Add edges between nodes at level i and level i+1
            for u,v in zip(p1, p2):
                G.add_edge(u,v)

    # Add edges between last level and sink node
    for node in levels[len(nNodesPerLevel)-1]:
        G.add_edge(node, current_node-1)

    return G

def save_network_structure (G: nx.DiGraph, filename: str) -> None:
    nx.write_gexf(G, f"{filename}.gexf")

def load_network (filename: str) -> nx.DiGraph:
    G = nx.read_gexf(f"{filename}.gexf")
    return G
#%%
if __name__ == "__main__":
    nNodes = [5, 10, 25, 40, 1]
    G = non_hierarchical_network(nNodes)
    print(f"Number of nodes: {G.number_of_nodes()}")
    print(f"Number of edges: {G.number_of_edges()}")

    # c_in_degree = 0
    # c_out_degree = 0
    # for node in G.nodes:
    #     # print(f"Node {node} is at level {G.nodes[node]['subset']}")
    #     # print(f"Node {node} has in-degree {G.in_degree(node)} and out-degree {G.out_degree(node)}, level = {G.nodes[node]['subset']}")
    #     in_degree = G.in_degree(node)
    #     out_degree = G.out_degree(node)
    #     if in_degree == 0:
    #         # print(f"Node {node} is a source node with out-degree {out_degree}")
    #         c_in_degree += 1
    #     elif out_degree == 0:
    #         # print(f"Node {node} is a sink node with in-degree {in_degree}")
    #         c_out_degree += 1
    # print(f"Number of source nodes: {c_in_degree}")
    # print(f"Number of sink nodes: {c_out_degree}")

    # # Draw the graph
    # pos = nx.multipartite_layout(G, subset_key="subset")  # Use the subset attribute for layout
    # nx.draw(G, pos, with_labels=True, node_size=500, node_color="skyblue", font_size=10, font_color="black")
    # plt.title("Hierarchical Network")
    # plt.show()
