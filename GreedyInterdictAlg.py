import os
import pandas as pd
import networkx as nx
from NetworkGen import *
from GurobiSolver import *
#%%
def greedy_alg (G: nx.DiGraph, name: str, B: int, unit_cost: bool, ml_model: str) -> list:
    # Get the predictions
    predictions = pd.read_csv(f"{name}.csv")
    # Sort predictions by "F_r" in a descending order for a given ML model
    predictions = predictions.sort_values(ml_model, ascending=False)
    if unit_cost:
        # Return top B arcs
        interdicted_arcs = predictions.head(B)["arc"].tolist()
        interdicted_arcs = [tuple(map(str, eval(arc))) for arc in interdicted_arcs]
    else:
        interdicted_arcs = []
        # Load the network
        b = nx.get_edge_attributes(G, 'c')
        for arc in predictions["arc"]:
            u, v = map(str, eval(arc))
            # Check if b_(u,v) is less than B
            if b[(u, v)] <= B:
                interdicted_arcs.append((u, v))
                B -= b[(u, v)]
    return interdicted_arcs

def find_max_flow (G: nx.DiGraph, name: str, path: str, B: int, interdicted_arcs: list, unit_cost: bool=True) -> gp.Model:
    m = create_model(G, name, B, unit_cost)
    # Add the interdiction constraints
    for u,v in interdicted_arcs:
        m.addConstr(m.getVarByName(f"z[{u},{v}]") == 1)
    # Update and solve the model
    m.update()
    m.optimize()
    # Save the model
    for format in ["mps", "sol", "lp", "json"]:
        m.write(f"{path}/{format}/{m.ModelName}.{format}")
    return m
#%%
if __name__ == "__main__":
    # Initialize directories
    data = "Test"
    ml_alg = "dt"
    parent_dir = os.path.dirname(os.getcwd())
    network_dir = os.path.join(parent_dir, "Networks", data)
    predictions_dir = os.path.join(parent_dir, "Predictions", ml_alg, data)
    models_dir = os.path.join(parent_dir, "Models-ml", ml_alg, data)
    os.makedirs(models_dir, exist_ok=True)
    # Load the network structure
    name, ext = "network_1_1.gexf".split('.')
    G = nx.read_gexf(f"{network_dir}/{name}.{ext}")
    # Initialize parameters
    B = 5
    unit_cost = True
    tag = "U" if unit_cost else ""
    # Make directories
    model_dir = os.path.join(models_dir, f"Model_{B}{tag}")
    for format in ["mps", "sol", "lp", "json"]:
        os.makedirs(f"{model_dir}/{format}", exist_ok=True)
    # Find the interdicted arcs
    interdicted_arcs = greedy_alg(G, f"{predictions_dir}/{name}", B, unit_cost, ml_alg)
    # Solve the model
    m = find_max_flow(G, name, model_dir, B, interdicted_arcs)
    print(f"Objective value: {m.objVal}")
    for var in m.getVars():
        if var.VarName.startswith("z") and var.X > 0:
            print(f"{var.VarName}: {var.X}")