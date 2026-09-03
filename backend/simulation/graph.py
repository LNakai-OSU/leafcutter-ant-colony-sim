"""
Builds the combined nest + foraging-trail graph.

Layout (see config.py for the qualitative sources): a single "entrance"
node sits at the surface and is the boundary between two subgraphs:

- The **nest** (domain="nest"): a queen chamber at the bottom of a main
  shaft, nursery chambers clustered near her, several fungus-garden
  chambers at mid-depth (the colony's food supply), and waste chambers
  placed deliberately apart from the fungus cluster - real Atta colonies
  keep refuse away from the gardens.
- The **surface trail network** (domain="surface"): trunk trails
  branching out from the entrance to scattered leaf-source trees, mirroring
  the trunk-and-branch trail systems Atta colonies cut through the
  understory to reach foraging sites, sometimes over many meters.

Positions are 3D (x, y, z) with z <= 0 underground and z == 0 at the
surface, purely so the frontend can render it as a literal underground/
aboveground graph.
"""

import math

import networkx as nx

from . import config


def _polar_offset(radius, angle_deg, z):
    rad = math.radians(angle_deg)
    return (radius * math.cos(rad), radius * math.sin(rad), z)


def _dist(a, b):
    return math.dist(a, b)


def build_colony_graph(rng) -> nx.Graph:
    G = nx.Graph()

    def add(node_id, kind, pos, domain, **attrs):
        G.add_node(node_id, kind=kind, domain=domain, pos=pos, **attrs)

    add("entrance", "entrance", (0.0, 0.0, 0.0), "boundary")

    add("shaft", "junction", (0.0, 0.0, -2.2), "nest")
    G.add_edge("entrance", "shaft")

    add("queen_access", "junction", (1.0, 0.0, -6.0), "nest")
    G.add_edge("shaft", "queen_access")
    add("queen", "queen", (0.0, 0.0, -8.5), "nest")
    G.add_edge("queen_access", "queen")

    for i in range(config.NUM_NURSERY_CHAMBERS):
        angle = 40 + i * (280 / max(config.NUM_NURSERY_CHAMBERS, 1))
        pos = _polar_offset(2.4 + rng.random(), angle, -6.5 - rng.random())
        node_id = f"nursery_{i}"
        add(node_id, "nursery", pos, "nest", brood=6 + i)
        G.add_edge("queen_access", node_id)

    for i in range(config.NUM_FUNGUS_CHAMBERS):
        angle = i * (360 / config.NUM_FUNGUS_CHAMBERS)
        radius = 3.0 + rng.random() * 1.5
        depth = -3.0 - rng.random() * 2.5
        pos = _polar_offset(radius, angle, depth)
        node_id = f"fungus_{i}"
        add(node_id, "fungus", pos, "nest", health=config.FUNGUS_MAX_HEALTH * 0.6)
        G.add_edge("shaft", node_id)

    for i in range(config.NUM_WASTE_CHAMBERS):
        angle = 200 + i * 40
        pos = _polar_offset(5.5, angle, -10.0 - i)
        node_id = f"waste_{i}"
        add(node_id, "waste", pos, "nest", fill=0.0)
        G.add_edge("shaft", node_id)

    for i in range(config.NUM_JUNCTION_CHAMBERS):
        angle = i * (360 / config.NUM_JUNCTION_CHAMBERS) + 30
        pos = _polar_offset(4.2, angle, -1.5 - rng.random() * 3)
        node_id = f"junction_{i}"
        add(node_id, "junction", pos, "nest")
        G.add_edge("shaft", node_id)
        nearby_fungus = f"fungus_{i % config.NUM_FUNGUS_CHAMBERS}"
        G.add_edge(node_id, nearby_fungus)

    trunk_ids = []
    for i in range(config.NUM_TRUNK_JUNCTIONS):
        angle = i * (360 / config.NUM_TRUNK_JUNCTIONS)
        pos = _polar_offset(7.0, angle, 0.15)
        node_id = f"trunk_{i}"
        add(node_id, "trunk", pos, "surface")
        G.add_edge("entrance", node_id, pheromone=config.PHEROMONE_MIN)
        trunk_ids.append(node_id)

    for i in range(config.NUM_LEAF_TREES):
        angle = rng.random() * 360
        radius = rng.uniform(config.TREE_MIN_RADIUS, config.TREE_MAX_RADIUS)
        pos = _polar_offset(radius, angle, 0.0)
        node_id = f"tree_{i}"
        add(
            node_id,
            "tree",
            pos,
            "surface",
            biomass=config.TREE_MAX_BIOMASS * rng.uniform(0.5, 1.0),
            quality=rng.uniform(0.6, 1.0),
        )
        trunk = min(trunk_ids, key=lambda t: _dist(G.nodes[t]["pos"], pos))
        G.add_edge(trunk, node_id, pheromone=config.PHEROMONE_MIN)

    for i in range(len(trunk_ids)):
        a, b = trunk_ids[i], trunk_ids[(i + 1) % len(trunk_ids)]
        if not G.has_edge(a, b):
            G.add_edge(a, b, pheromone=config.PHEROMONE_MIN)

    for u, v in G.edges():
        if "pheromone" not in G.edges[u, v]:
            G.edges[u, v]["pheromone"] = 0.0

    return G
