import os
from tqdm import tqdm
import networkx as nx
import gurobipy as gp
from gurobipy import GRB
#%%
def create_model (G: nx.DiGraph, name: str, B: int, unit_cost: bool) -> gp.Model:
    # Parameters
    c = nx.get_edge_attributes(G, "c")
    b = nx.get_edge_attributes(G, "b")
    s = str(0)
    t = str(G.number_of_nodes() - 1)

    # Initialize the model
    env = gp.Env(empty=True)
    env.setParam('OutputFlag', 0) # suppress Gurobi output
    env.setParam('TimeLimit', 60*60) # set the time limit to 60 minutes
    env.start()
    m = gp.Model(name, env) # model constructor

    # Decision variables
    beta = m.addVars(G.edges, vtype=GRB.BINARY, name="beta")
    z = m.addVars(G.edges, vtype=GRB.BINARY, name="z")
    pi = m.addVars(G.nodes, vtype=GRB.BINARY, name="pi")

    # Objective function
    obj = gp.quicksum(c[u,v] * beta[u,v] for u,v in G.edges)
    m.setObjective(obj, GRB.MINIMIZE)

    # Constraints
    constr1 = m.addConstrs((beta[u,v] + z[u,v] + pi[u] - pi[v] >= 0 for u,v in G.edges), name="constr1")
    constr2 = m.addConstr(pi[t] - pi[s] >= 1, name="constr2")
    if unit_cost:
        constr3 = m.addConstr((gp.quicksum(z[u,v] for u,v in G.edges) <= B), name="constr3")
    else:
        constr3 = m.addConstr((gp.quicksum(b[u,v] * z[u,v] for u,v in G.edges) <= B), name="constr3")

    # Update the model
    m.update()

    return m

def solve_model (filename: str, path: str, B:int, unit_cost: bool) -> gp.Model:
    # Create the model
    m = create_model(G, filename, B, unit_cost)
    # Optimize the model
    m.optimize()
    # Save the model
    for format in ["mps", "sol", "lp", "json"]:
        m.write(f"{path}/{format}/{m.ModelName}.{format}")
    return m

def load_model (filename: str, path: str, format: str) -> gp.Model:
    m = gp.read(f"{path}/{filename}.{format}")
    return m
#%%
if __name__ == "__main__":
    # Initialize directories
    parent_dir = os.path.dirname(os.getcwd())
    network_dir = os.path.join(parent_dir, "Networks")
    models_dir = os.path.join(parent_dir, "Models")
    os.makedirs(models_dir, exist_ok=True)

    # Initialize parameters
    small_uc_B = [i for i in range(1, 9+1)]
    small_B = [5, 10, 20, 30, 40, 80, 120, 150, 200]

    large_uc_B = [1, 10, 50, 100, 500, 1000, 2000, 2500, 3000]
    large_B = [5, 100, 200, 500, 1000, 2000, 3000, 4000, 5000, 7500, 10000, 15000, 20000]

    # Solve instances
    for f in tqdm(os.listdir(network_dir)):
        name, ext = f.split('.')
        G = nx.read_gexf(f"{network_dir}/{name}.{ext}")
        for unit_cost in [True, False]:
            if unit_cost:
                tag = "U"
                if name.split('_')[1] in map(str, [6, 7, 8]):
                    B_vals = large_uc_B
                else:
                    B_vals = small_uc_B
            else:
                tag = ""
                if name.split('_')[1] in map(str, [6, 7, 8]):
                    B_vals = large_B
                else:
                    B_vals = small_B
            for B in B_vals:
                # Make directories
                model_dir = os.path.join(models_dir, f"Model_{B}{tag}")
                for format in ["mps", "sol", "lp", "json"]:
                    os.makedirs(f"{model_dir}/{format}", exist_ok=True)
                # Solve the model
                m = solve_model(name, model_dir, B, unit_cost)


    # # Load the network structure
    # name, ext = "network_1_1.gexf".split('.')
    # G = nx.read_gexf(f"{network_dir}/{name}.{ext}")
    # # Initialize parameters
    # B = 5
    # unit_cost = True
    # tag = "U" if unit_cost else ""
    # # Make directories
    # model_dir = os.path.join(models_dir, f"Model_{B}{tag}")
    # for format in ["mps", "sol", "lp", "json"]:
    #     os.makedirs(f"{model_dir}/{format}", exist_ok=True)
    # # Solve the model
    # m = solve_model(name, model_dir, B, unit_cost)
    # print(f"Objective value: {m.objVal}")
    # for var in m.getVars():
    #     if var.VarName.startswith("z") and var.X > 0:
    #         print(f"{var.VarName}: {var.X}")