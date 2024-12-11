import random
import networkx as nx
import matplotlib.pyplot as plt
#%%
def generate_network (nLevels: int, nNodesPerLevel: list, nArcs: int, type: str, seed: int = 42):
    assert nLevels == len(nNodesPerLevel), "nNodes must have length equal to nLevels"
    random.seed(seed)
    G = nx.DiGraph()  # Create a directed graph

    # Add nodes at each level
    current_node = 0
    levels = []

    # Source node
    levels.append([0])
    G.add_node(current_node, subset=0)
    current_node += 1

    # Intermediate nodes
    for level in range(1, nLevels+1):
        level_nodes = list(range(current_node, current_node + nNodesPerLevel[level-1]))
        levels.append(level_nodes)
        for node in level_nodes:
            G.add_node(node, subset=level)  # Assign subset attribute
        current_node += nNodesPerLevel[level-1]

    # Sink node
    levels.append([current_node])
    G.add_node(current_node, subset=nLevels+1)

    # Number of edges at each level
    min_nEdges = nNodesPerLevel[0] + nNodesPerLevel[-1] + sum(max(nNodesPerLevel[i], nNodesPerLevel[i+1]) for i in range(nLevels-1))
    if type == "H":
        nEdges_pair = [max(nNodesPerLevel[i], nNodesPerLevel[i+1]) + (nArcs - min_nEdges) // (nLevels-1) for i in range(nLevels-1)]
        print(f"Number of edges per pair of levels: {nEdges_pair}")
        # Adjust the number of edges to match the total number of edges
        if sum(nEdges_pair) + nNodesPerLevel[0] + nNodesPerLevel[-1] < nArcs:
            nEdges_pair[-1] += nArcs - sum(nEdges_pair) - nNodesPerLevel[0] - nNodesPerLevel[-1]
        else:
            nEdges_pair[-1] -= sum(nEdges_pair) + nNodesPerLevel[0] + nNodesPerLevel[-1] - nArcs
        print(f"Number of edges per pair of levels: {nEdges_pair}")
        # print(f"Total number of edges: {sum(nEdges_pair)} + {nNodesPerLevel[0]} + {nNodesPerLevel[-1]}")
    else:
        nEdges_pair = [max(nNodesPerLevel[i], nNodesPerLevel[i+1]) for i in range(nLevels-1)]
        excess_edges = min_nEdges - nArcs

    # Add edges between source node and the first level
    for node in levels[1]:
        G.add_edge(0, node)

    # Add edges between intermediate nodes
    for level in range(1, nLevels):
        p1 = levels[level] # Nodes at level i
        p2 = levels[level+1] # Nodes at level i+1
        nEdges = nEdges_pair[level-1] # Number of edges between level i and level i+1
        # Add dummy nodes at each levels i and i+1 to match the number of required edges
        while len(p1) < nEdges:
            p1 += p1[:nEdges-len(p1)]
        while len(p2) < nEdges:
            p2 += p2[:nEdges-len(p2)]
        # Randomly shuffle the nodes at each level to create the required number edges
        while len(set(zip(p1, p2))) < nEdges:
            random.shuffle(p1)
            random.shuffle(p2)
        # Add edges between nodes at level i and level i+1
        for i,j in zip(p1, p2):
            G.add_edge(i,j)

    # Add edges between last level and sink node
    for node in levels[-2]:
        G.add_edge(node, current_node)

    # Conver to a non-hierarchical network
    if type == "NH":
        for i in range(1, nLevels):
            for node in levels[i]:
                print(G.in_degree(node), G.out_degree(node))



        # nodes = list(G.nodes).copy()
        # nodes.remove(0)
        # nodes.remove(current_node)
        # while excess_edges > 0:
        #     i = random.choice(nodes) # Randomly select a node
        #     nodes.remove(i)
        #     print(i, excess_edges)
        #     paths = list(nx.all_simple_paths(G, source=0, target=i)).copy() # Find all paths from source to the selected node
        #     print(paths)
        #     for path in paths:
        #         print(i, path)
        #         if excess_edges > -1:
        #             for u, v in zip(path[:-1], path[1:]):
        #                 if excess_edges > -1:
        #                     G.remove_edge(u, v)
        #                     excess_edges -= 1
        #                 else:
        #                     i = v
        #                     break
        #         else:
        #             break
        #     G.add_edge(0, i)
        #     print((0, i))
        #     excess_edges += 1

    return G


#%%
# Example usage
nLevels = 4
nNodes = [12, 50, 200, 410]
nArcs = 876
type = "NH"
G = generate_network(nLevels, nNodes, nArcs, type)
print(f"Number of nodes: {G.number_of_nodes()}")
print(f"Number of edges: {G.number_of_edges()}")
# print(list(nx.all_simple_paths(G, source=0, target=231)))

# c_in_degree = 0
# c_out_degree = 0
# for node in G.nodes:
#     # print(f"Node {node} has in-degree {G.in_degree(node)} and out-degree {G.out_degree(node)}")
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
