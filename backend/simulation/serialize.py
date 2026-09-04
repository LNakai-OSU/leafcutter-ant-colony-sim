"""Flattens the model's live graph/agent state into plain JSON-able dicts."""


def serialize_graph(model):
    nodes = []
    for node_id, d in model.graph.nodes(data=True):
        entry = {
            "id": node_id,
            "kind": d["kind"],
            "domain": d["domain"],
            "pos": list(d["pos"]),
            "colony": d.get("colony"),
        }
        if d["kind"] == "fungus":
            entry["health"] = round(d["health"], 1)
            entry["infection"] = round(d.get("infection", 0.0), 3)
        if d["kind"] == "tree":
            entry["biomass"] = round(d["biomass"], 1)
            entry["quality"] = round(d["quality"], 2)
            entry["acceptance"] = round(d.get("acceptance", 1.0), 2)
            entry["dead"] = d.get("dead", False)
        if d["kind"] == "nursery":
            entry["brood"] = d["brood"]
        nodes.append(entry)

    edges = []
    for u, v, d in model.graph.edges(data=True):
        edges.append(
            {
                "source": u,
                "target": v,
                "pheromone": round(d.get("pheromone", 0.0), 4),
                "surface": model.graph.nodes[u]["domain"] == "surface" or model.graph.nodes[v]["domain"] == "surface",
            }
        )
    return nodes, edges


def serialize_ants(model):
    out = []
    for a in model.schedule.agents:
        out.append(
            {
                "id": a.unique_id,
                "caste": a.caste,
                "colony": a.colony,
                "task": a.task,
                "phase": a.phase.value if hasattr(a.phase, "value") else a.phase,
                "node": a.node,
                "edge": list(a.edge) if a.edge else None,
                "t": round(a.t, 3),
                "carrying": round(a.carrying, 2),
            }
        )
    return out


def serialize_state(model):
    nodes, edges = serialize_graph(model)
    return {
        "tick": model.tick,
        "cfg": model.cfg,
        "colonies": [c["id"] for c in model.colonies],
        "season_multiplier": round(model.season_multiplier, 3),
        "raining": model.raining,
        "nodes": nodes,
        "edges": edges,
        "ants": serialize_ants(model),
        "stats": model.history[-1] if model.history else None,
    }
