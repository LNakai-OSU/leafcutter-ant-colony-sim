import mesa

from . import config
from .agents import Ant
from .graph import build_colony_graph


class ColonyModel(mesa.Model):
    def __init__(self, seed=None):
        super().__init__(seed=seed)
        self.graph = build_colony_graph(self.random)
        self.schedule = mesa.time.RandomActivation(self)
        self.tick = 0
        self.leaves_delivered = 0.0
        self.history = []

        nodes = self.graph.nodes(data=True)
        self.fungus_nodes = [n for n, d in nodes if d["kind"] == "fungus"]
        self.nursery_nodes = [n for n, d in nodes if d["kind"] == "nursery"]
        self.waste_nodes = [n for n, d in nodes if d["kind"] == "waste"]
        self.trunk_nodes = [n for n, d in nodes if d["kind"] == "trunk"]

        self._next_id = 0
        for caste, count in config.STARTING_COLONY.items():
            for _ in range(count):
                self._spawn_ant(caste)

        self._record_history()

    # -- setup ---------------------------------------------------------
    def _home_for_caste(self, caste):
        if caste == "minim":
            return self.random.choice(self.nursery_nodes + self.fungus_nodes)
        if caste == "minor":
            return self.random.choice(self.waste_nodes + self.fungus_nodes)
        if caste == "media":
            return self.random.choice(self.fungus_nodes)
        if caste == "major":
            return self.random.choice(self.trunk_nodes + ["entrance"])
        return "entrance"

    def _spawn_ant(self, caste):
        ant = Ant(self._next_id, self, caste, self._home_for_caste(caste))
        self._next_id += 1
        self.schedule.add(ant)
        return ant

    # -- per-tick colony-level dynamics ---------------------------------
    def _caste_probs(self):
        pop = self.schedule.get_agent_count()
        probs = config.CASTE_CURVE[0][1]
        for threshold, p in config.CASTE_CURVE:
            if pop >= threshold:
                probs = p
        return probs

    def _maybe_birth(self):
        if self.schedule.get_agent_count() >= config.MAX_POPULATION:
            return
        chambers = [self.graph.nodes[n] for n in self.fungus_nodes]
        avg_health = sum(c["health"] for c in chambers) / len(chambers)
        if avg_health < config.BIRTH_FUNGUS_SURPLUS_THRESHOLD:
            return
        if self.random.random() > config.BIRTH_CHANCE_PER_TICK:
            return
        probs = self._caste_probs()
        castes, weights = zip(*probs.items())
        caste = self.random.choices(castes, weights=weights, k=1)[0]
        self._spawn_ant(caste)
        cost_each = config.BIRTH_FUNGUS_COST / len(chambers)
        for c in chambers:
            c["health"] = max(0.0, c["health"] - cost_each)

    def _decay_pheromone(self):
        for u, v, data in self.graph.edges(data=True):
            if self.graph.nodes[u]["domain"] == "surface" or self.graph.nodes[v]["domain"] == "surface":
                data["pheromone"] = max(config.PHEROMONE_MIN, data["pheromone"] * config.PHEROMONE_EVAPORATION)

    def _fungus_upkeep(self):
        for n in self.fungus_nodes:
            chamber = self.graph.nodes[n]
            chamber["health"] = max(0.0, chamber["health"] - config.FUNGUS_UPKEEP_PER_TICK)

    def _regrow_trees(self):
        for _, d in self.graph.nodes(data=True):
            if d["kind"] == "tree":
                d["biomass"] = min(config.TREE_MAX_BIOMASS, d["biomass"] + config.TREE_REGROWTH_PER_TICK)

    def step(self):
        self.schedule.step()
        self._decay_pheromone()
        self._fungus_upkeep()
        self._regrow_trees()
        self._maybe_birth()
        self.tick += 1
        self._record_history()

    def _record_history(self):
        pop_by_caste = {"minim": 0, "minor": 0, "media": 0, "major": 0}
        for a in self.schedule.agents:
            pop_by_caste[a.caste] += 1
        avg_fungus = sum(self.graph.nodes[n]["health"] for n in self.fungus_nodes) / len(self.fungus_nodes)
        self.history.append(
            {
                "tick": self.tick,
                "population": dict(pop_by_caste),
                "total_population": sum(pop_by_caste.values()),
                "avg_fungus_health": avg_fungus,
                "leaves_delivered": round(self.leaves_delivered, 2),
            }
        )
        if len(self.history) > 500:
            self.history = self.history[-500:]
