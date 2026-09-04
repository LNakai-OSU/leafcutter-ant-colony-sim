"""
Builds the combined nest + foraging-trail graph.

Layout (see config.py / README for the qualitative sources): each colony
has an "entrance" node at the surface, the boundary between two subgraphs -
a **nest** (queen chamber, nursery, fungus gardens, waste chambers kept
apart from the fungus cluster) and a **surface trail network** (trunk
trails branching out to leaf-source trees). With `rival_colony` on, two
full nest structures are built at opposite offsets and trees near the
midpoint get a trail edge to *both* colonies' nearest trunk - a shared,
contested resource - while trees closer to one side are effectively
exclusive to it.

Positions are 3D (x, y, z) with z <= 0 underground and z == 0 at the
surface, so the frontend can render it as a literal underground/aboveground
graph.
"""

import math

import networkx as nx

from . import config


def _polar_offset(center, radius, angle_deg, z):
    rad = math.radians(angle_deg)
    return (center[0] + radius * math.cos(rad), center[1] + radius * math.sin(rad), z)


def _dist(a, b):
    return math.dist(a, b)


def _build_nest(G, rng, colony_id, center):
    """Builds one colony's underground nest + trunk junctions, returns its metadata."""
    entrance = f"entrance_{colony_id}"
    G.add_node(entrance, kind="entrance", domain="boundary", pos=_polar_offset(center, 0, 0, 0.0), colony=colony_id)

    shaft = f"shaft_{colony_id}"
    G.add_node(shaft, kind="junction", domain="nest", pos=_polar_offset(center, 0, 0, -2.2), colony=colony_id)
    G.add_edge(entrance, shaft)

    queen_access = f"queen_access_{colony_id}"
    G.add_node(queen_access, kind="junction", domain="nest", pos=_polar_offset(center, 1.0, 0, -6.0), colony=colony_id)
    G.add_edge(shaft, queen_access)

    queen = f"queen_{colony_id}"
    G.add_node(queen, kind="queen", domain="nest", pos=_polar_offset(center, 0, 0, -8.5), colony=colony_id)
    G.add_edge(queen_access, queen)

    nursery_nodes = []
    for i in range(config.NUM_NURSERY_CHAMBERS):
        angle = 40 + i * (280 / max(config.NUM_NURSERY_CHAMBERS, 1))
        pos = _polar_offset(center, 2.4 + rng.random(), angle, -6.5 - rng.random())
        node_id = f"nursery_{colony_id}_{i}"
        G.add_node(node_id, kind="nursery", domain="nest", pos=pos, colony=colony_id, brood=6 + i)
        G.add_edge(queen_access, node_id)
        nursery_nodes.append(node_id)

    fungus_nodes = []
    for i in range(config.NUM_FUNGUS_CHAMBERS):
        angle = i * (360 / config.NUM_FUNGUS_CHAMBERS)
        radius = 3.0 + rng.random() * 1.5
        depth = -3.0 - rng.random() * 2.5
        pos = _polar_offset(center, radius, angle, depth)
        node_id = f"fungus_{colony_id}_{i}"
        G.add_node(
            node_id, kind="fungus", domain="nest", pos=pos, colony=colony_id,
            health=config.FUNGUS_MAX_HEALTH * 0.6, infection=0.0,
        )
        G.add_edge(shaft, node_id)
        fungus_nodes.append(node_id)

    waste_nodes = []
    for i in range(config.NUM_WASTE_CHAMBERS):
        angle = 200 + i * 40
        pos = _polar_offset(center, 5.5, angle, -10.0 - i)
        node_id = f"waste_{colony_id}_{i}"
        G.add_node(node_id, kind="waste", domain="nest", pos=pos, colony=colony_id, fill=0.0)
        G.add_edge(shaft, node_id)
        waste_nodes.append(node_id)

    for i in range(config.NUM_JUNCTION_CHAMBERS):
        angle = i * (360 / config.NUM_JUNCTION_CHAMBERS) + 30
        pos = _polar_offset(center, 4.2, angle, -1.5 - rng.random() * 3)
        node_id = f"junction_{colony_id}_{i}"
        G.add_node(node_id, kind="junction", domain="nest", pos=pos, colony=colony_id)
        G.add_edge(shaft, node_id)
        G.add_edge(node_id, fungus_nodes[i % len(fungus_nodes)])

    trunk_nodes = []
    for i in range(config.NUM_TRUNK_JUNCTIONS):
        angle = i * (360 / config.NUM_TRUNK_JUNCTIONS)
        pos = _polar_offset(center, 7.0, angle, 0.15)
        node_id = f"trunk_{colony_id}_{i}"
        G.add_node(node_id, kind="trunk", domain="surface", pos=pos, colony=colony_id)
        G.add_edge(entrance, node_id, pheromone=config.PHEROMONE_MIN)
        trunk_nodes.append(node_id)
    for i in range(len(trunk_nodes)):
        a, b = trunk_nodes[i], trunk_nodes[(i + 1) % len(trunk_nodes)]
        if not G.has_edge(a, b):
            G.add_edge(a, b, pheromone=config.PHEROMONE_MIN)

    return {
        "id": colony_id,
        "entrance": entrance,
        "queen": queen,
        "fungus_nodes": fungus_nodes,
        "nursery_nodes": nursery_nodes,
        "waste_nodes": waste_nodes,
        "trunk_nodes": trunk_nodes,
        "center": center,
    }


def _tree_angle_radius(rng, cfg, cluster_centers):
    if cfg["tree_layout"] == "patchy" and cluster_centers:
        base_angle = rng.choice(cluster_centers)
        angle = base_angle + rng.uniform(-config.PATCH_JITTER_DEG, config.PATCH_JITTER_DEG)
    else:
        angle = rng.random() * 360
    radius = rng.uniform(config.TREE_MIN_RADIUS, config.TREE_MAX_RADIUS)
    return angle, radius


def build_colony_graph(rng, cfg):
    G = nx.Graph()

    if cfg["rival_colony"]:
        colonies = [
            _build_nest(G, rng, "A", (-config.RIVAL_OFFSET / 2, 0.0)),
            _build_nest(G, rng, "B", (config.RIVAL_OFFSET / 2, 0.0)),
        ]
        tree_center = (0.0, 0.0)
    else:
        colonies = [_build_nest(G, rng, "A", (0.0, 0.0))]
        tree_center = (0.0, 0.0)

    cluster_centers = None
    if cfg["tree_layout"] == "patchy":
        cluster_centers = [rng.random() * 360 for _ in range(config.PATCH_CLUSTER_COUNT)]

    all_trunks = [(c["id"], t) for c in colonies for t in c["trunk_nodes"]]

    for i in range(cfg["num_leaf_trees"]):
        angle, radius = _tree_angle_radius(rng, cfg, cluster_centers)
        pos = _polar_offset(tree_center, radius, angle, 0.0)
        node_id = f"tree_{i}"
        acceptance = rng.uniform(0.35, 1.0) if cfg["chemical_defense"] else 1.0
        G.add_node(
            node_id, kind="tree", domain="surface", pos=pos,
            biomass=config.TREE_MAX_BIOMASS * rng.uniform(0.5, 1.0),
            quality=rng.uniform(0.6, 1.0),
            acceptance=acceptance,
            dead=False,
            depleted_ticks=0,
        )

        if len(colonies) == 1:
            trunk = min(all_trunks, key=lambda ct: _dist(G.nodes[ct[1]]["pos"], pos))[1]
            G.add_edge(trunk, node_id, pheromone=config.PHEROMONE_MIN)
        else:
            # connect to the nearest trunk of every colony within CONTESTED_RADIUS,
            # and always to the single overall nearest trunk (guarantees reachability)
            nearest = min(all_trunks, key=lambda ct: _dist(G.nodes[ct[1]]["pos"], pos))
            connected_colonies = {nearest[0]}
            G.add_edge(nearest[1], node_id, pheromone=config.PHEROMONE_MIN)
            for c in colonies:
                if c["id"] in connected_colonies:
                    continue
                nearest_for_c = min(c["trunk_nodes"], key=lambda t: _dist(G.nodes[t]["pos"], pos))
                if _dist(G.nodes[nearest_for_c]["pos"], pos) <= config.CONTESTED_RADIUS:
                    G.add_edge(nearest_for_c, node_id, pheromone=config.PHEROMONE_MIN)
                    connected_colonies.add(c["id"])

    for u, v in G.edges():
        if "pheromone" not in G.edges[u, v]:
            G.edges[u, v]["pheromone"] = 0.0

    return G, colonies
