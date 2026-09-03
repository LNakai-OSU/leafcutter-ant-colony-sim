"""
Ant agent behavior.

Caste -> task mapping is a simplification of real Atta division of labor:
minims (smallest) tend brood and the fungus garden and rarely leave the
nest; minors handle waste and back up fungus tending; mediae are the
colony's primary leaf-cutting foragers; majors are the largest caste and
mostly hold position near the nest entrance/trunk trails (a stand-in for
their real role in defense and clearing major trail obstructions).
Movement inside the nest uses shortest-path routing (an ant "knows its way
home"); movement on the surface trail network is a pheromone-biased random
walk, i.e. an ant-colony-optimization-style rule where an edge with
concentration p is chosen with probability proportional to p**alpha, with
a small flat exploration chance so unmarked trails still get sampled -
this is what produces trail formation/reinforcement over time.
"""

from collections import deque
from enum import Enum

import mesa
import networkx as nx

from . import config


class Phase(str, Enum):
    IDLE = "idle"
    TO_ENTRANCE = "to_entrance"
    TO_TREE = "to_tree"
    CUTTING = "cutting"
    RETURNING = "returning"
    TO_FUNGUS = "to_fungus"
    DEPOSITING = "depositing"


def initial_task(caste, rng):
    return {
        "minim": rng.choice(["nurse", "fungus_tend"]),
        "minor": rng.choice(["waste", "fungus_tend"]),
        "media": "forage",
        "major": "guard",
    }[caste]


class Ant(mesa.Agent):
    def __init__(self, unique_id, model, caste, home_node):
        super().__init__(unique_id, model)
        self.caste = caste
        self.home_node = home_node
        self.node = home_node
        self.task = initial_task(caste, model.random)
        self.phase = Phase.IDLE
        self.queue = deque()
        self.edge = None  # (from, to) currently being crossed
        self.t = 0.0
        self.carrying = 0.0
        self.tree_quality = 1.0
        self.trail_history = []
        self.rest_ticks = model.random.randint(0, 4)

    # -- generic movement -----------------------------------------------
    def _speed(self):
        return config.EDGE_SPEED[self.caste]

    def _start_path(self, path):
        """`path` is a node-id list beginning with the ant's current node."""
        self.queue = deque(path[1:])
        self.edge = None
        self._advance_queue()

    def _advance_queue(self):
        if self.queue:
            nxt = self.queue.popleft()
            self.edge = (self.node, nxt)
            self.t = 0.0
        else:
            self.edge = None

    def _step_edge(self):
        """Advance across the current edge. Returns True on arrival."""
        if self.edge is None:
            return True
        self.t += self._speed()
        if self.t >= 1.0:
            self.node = self.edge[1]
            self.edge = None
            self.t = 0.0
            return True
        return False

    def _travel_step(self):
        """Drive the queue-based path follower one tick. Returns True once
        the whole path (set by _start_path) has been completed."""
        if self.edge is not None:
            if not self._step_edge():
                return False
        if self.queue:
            self._advance_queue()
            return False
        return True

    # -- dispatch ----------------------------------------------------------
    def step(self):
        if self.task == "forage":
            self._step_forage()
        else:
            self._step_stationary()

    # -- nurses / fungus tenders / waste managers / guards ------------------
    def _step_stationary(self):
        if self.edge is not None:
            self._step_edge()
            return
        if self.task == "fungus_tend" and self.model.graph.nodes[self.node]["kind"] == "fungus":
            chamber = self.model.graph.nodes[self.node]
            chamber["health"] = min(config.FUNGUS_MAX_HEALTH, chamber["health"] + 0.05)

        if self.rest_ticks > 0:
            self.rest_ticks -= 1
            return

        g = self.model.graph
        if self.node == self.home_node and self.model.random.random() < 0.15:
            neighbors = [n for n in g.neighbors(self.node) if g.nodes[n]["domain"] != "surface"]
            if neighbors:
                self._start_path([self.node, self.model.random.choice(neighbors)])
        elif self.node != self.home_node:
            self._start_path(nx.shortest_path(g, self.node, self.home_node))
        self.rest_ticks = self.model.random.randint(2, 5)

    # -- foraging state machine --------------------------------------------
    def _step_forage(self):
        g = self.model.graph

        if self.phase == Phase.IDLE:
            self._start_path(nx.shortest_path(g, self.node, "entrance"))
            self.phase = Phase.TO_ENTRANCE
            return

        if self.phase == Phase.TO_ENTRANCE:
            if self._travel_step():
                self.trail_history = []
                self.phase = Phase.TO_TREE
            return

        if self.phase == Phase.TO_TREE:
            if self.edge is not None:
                if self._step_edge() and g.nodes[self.node]["kind"] == "tree":
                    self.phase = Phase.CUTTING
                return
            self._choose_surface_hop()
            return

        if self.phase == Phase.CUTTING:
            self._cut_leaf()
            return

        if self.phase == Phase.RETURNING:
            if self._travel_step():
                self._deposit_pheromone_trail()
                fungus_id = self.model.random.choice(self.model.fungus_nodes)
                self._start_path(nx.shortest_path(g, "entrance", fungus_id))
                self.phase = Phase.TO_FUNGUS
            return

        if self.phase == Phase.TO_FUNGUS:
            if self._travel_step():
                self.phase = Phase.DEPOSITING
            return

        if self.phase == Phase.DEPOSITING:
            self._deposit_leaf()
            return

    def _choose_surface_hop(self):
        g = self.model.graph
        neighbors = [n for n in g.neighbors(self.node) if g.nodes[n]["domain"] != "nest"]
        if len(neighbors) > 1 and self.trail_history:
            came_from = self.trail_history[-1][0]
            if len(neighbors) > 1 and came_from in neighbors:
                neighbors = [n for n in neighbors if n != came_from] or neighbors

        weights = [
            max(g.edges[self.node, n].get("pheromone", config.PHEROMONE_MIN), config.PHEROMONE_MIN)
            ** config.PHEROMONE_ALPHA
            for n in neighbors
        ]
        total = sum(weights)
        if total <= 0 or self.model.random.random() < config.EXPLORATION_FLOOR:
            choice = self.model.random.choice(neighbors)
        else:
            r = self.model.random.random() * total
            acc = 0.0
            choice = neighbors[-1]
            for n, w in zip(neighbors, weights):
                acc += w
                if r <= acc:
                    choice = n
                    break

        self.trail_history.append((self.node, choice))
        self.edge = (self.node, choice)
        self.t = 0.0

    def _cut_leaf(self):
        g = self.model.graph
        tree = g.nodes[self.node]
        amount = min(tree["biomass"], config.LEAF_CUT_AMOUNT.get(self.caste, 3.0))
        tree["biomass"] -= amount
        self.carrying = amount
        self.tree_quality = tree["quality"]

        outbound_nodes = [self.trail_history[0][0]] + [v for _, v in self.trail_history]
        self._start_path(list(reversed(outbound_nodes)))
        self.phase = Phase.RETURNING

    def _deposit_pheromone_trail(self):
        g = self.model.graph
        deposit = self.carrying * self.tree_quality * config.PHEROMONE_DEPOSIT_SCALE
        for u, v in self.trail_history:
            g.edges[u, v]["pheromone"] = min(1.0, g.edges[u, v]["pheromone"] + deposit)
        self.trail_history = []

    def _deposit_leaf(self):
        g = self.model.graph
        chamber = g.nodes[self.node]
        chamber["health"] = min(
            config.FUNGUS_MAX_HEALTH,
            chamber["health"] + self.carrying * config.FUNGUS_FEED_PER_LEAF_UNIT,
        )
        self.model.leaves_delivered += self.carrying
        self.carrying = 0.0
        self.phase = Phase.IDLE
