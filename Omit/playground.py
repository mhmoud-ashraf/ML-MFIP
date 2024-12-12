import networkx as nx
import random

# Parameters
levels = {1: 1, 2: 12, 3: 50, 4: 200, 5: 410, 6: 1}
total_arcs = 876

# Create a directed graph
G = nx.DiGraph()

# Create nodes for each level
node_labels = {}
current_node = 0
for level, count in levels.items():
    for _ in range(count):
        current_node += 1
        G.add_node(current_node, level=level)
        node_labels.setdefault(level, []).append(current_node)

# Connect the source to level 2 and level 5 to the sink
source = node_labels[1][0]
sink = node_labels[6][0]

for node in node_labels[2]:
    G.add_edge(source, node)

for node in node_labels[5]:
    G.add_edge(node, sink)

# Keep track of remaining arcs
used_arcs = G.number_of_edges()
remaining_arcs = total_arcs - used_arcs

# Ensure basic connectivity: Each node has at least one incoming and outgoing edge
for level in range(2, 6):  # Levels 2 to 5
    for node in node_labels[level]:
        if not list(G.predecessors(node)):  # No incoming edges
            pred = random.choice(node_labels[level - 1])
            if not G.has_edge(pred, node):
                G.add_edge(pred, node)
                remaining_arcs -= 1
        if not list(G.successors(node)):  # No outgoing edges
            succ = random.choice(node_labels[level + 1])
            if not G.has_edge(node, succ):
                G.add_edge(node, succ)
                remaining_arcs -= 1

# Add random edges until the total number of arcs reaches the limit
while remaining_arcs > 0:
    level = random.randint(2, 5)
    u = random.choice(node_labels[level])
    v = random.choice(node_labels[level + 1])
    if not G.has_edge(u, v):  # Avoid duplicate arcs
        G.add_edge(u, v)
        remaining_arcs -= 1

# Verify the total number of arcs
assert G.number_of_edges() == total_arcs, f"The total number of arcs is {G.number_of_edges()}, not {total_arcs}!"

# Verify full connectivity
for node in node_labels[2:]:
    assert nx.has_path(G, source, node), f"Node {node} is not reachable from the source."
for node in node_labels[5]:
    assert nx.has_path(G, node, sink), f"Node {node} cannot reach the sink."

# Output the graph
print(f"Graph generated with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")



for node in G.nodes:
    print(f"Node {node} has in-degree {G.in_degree(node)} and out-degree {G.out_degree(node)}")
#%%
# path = os.path.join(parent_dir, "Models", "Model_1U")
# m = load_model("network_1_1", path)
# m.ObjVal
# for v in m.getVars():
#     if 'z' in v.VarName and v.x > 0:
#         print(v.varName, v.x)
# json_data = load_json("network_1_1", path)
# json_data["ObjVal"]
# sol_data = load_sol("network_1_1", path)
# for v in sol_data:
#     if 'z' in v and sol_data[v] > 0:
#         print(v, sol_data[v])
#%%
# network_dir = os.path.join(parent_dir, "Networks")
# G = nx.read_gexf(f"{network_dir}/{'network_1_1'}.{'gexf'}")
# N = list(G.nodes())
# sink = G.nodes[N[-1]]["subset"]
# node = G.nodes['0']["subset"]
# egde = ('0', '1')
# nx.get_edge_attributes(G, 'c')[egde]