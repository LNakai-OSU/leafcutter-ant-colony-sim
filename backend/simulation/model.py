import math

import mesa

from . import config
from .agents import Ant
from .graph import build_colony_graph
from .scenario import make_scenario


class ColonyModel(mesa.Model):
    def __init__(self, seed=None, scenario=None):
        super().__init__(seed=seed)
        self.cfg = make_scenario(scenario)
        self.graph, colonies = build_colony_graph(self.random, self.cfg)
        self.colonies = colonies
        self.colony_by_id = {c["id"]: c for c in colonies}
        self.tree_nodes = [n for n, d in self.graph.nodes(data=True) if d["kind"] == "tree"]

        self.schedule = mesa.time.RandomActivation(self)
        self.tick = 0
        self.leaves_delivered = {c["id"]: 0.0 for c in colonies}
        self.history = []

        # drought/season state
        self.season_multiplier = 1.0
        self.raining = False
        self._rain_ticks_left = 0

        if self.cfg["disease_enabled"]:
            for c in colonies:
                seed_chamber = self.graph.nodes[self.random.choice(c["fungus_nodes"])]
                seed_chamber["infection"] = 0.11

        self._next_id = 0
        founding_queens = max(1, int(self.cfg["founding_queens"]))
        for c in colonies:
            for caste, count in config.STARTING_COLONY.items():
                for _ in range(count * founding_queens):
                    self._spawn_ant(caste, c["id"])

        self._record_history()

    # -- setup ---------------------------------------------------------
    def _home_for_caste(self, caste, colony_id):
        c = self.colony_by_id[colony_id]
        if caste == "minim":
            return self.random.choice(c["nursery_nodes"] + c["fungus_nodes"])
        if caste == "minor":
            return self.random.choice(c["waste_nodes"] + c["fungus_nodes"])
        if caste == "media":
            return self.random.choice(c["fungus_nodes"])
        if caste == "major":
            return self.random.choice(c["trunk_nodes"] + [c["entrance"]])
        return c["entrance"]

    def _spawn_ant(self, caste, colony_id):
        ant = Ant(self._next_id, self, caste, self._home_for_caste(caste, colony_id), colony_id)
        self._next_id += 1
        self.schedule.add(ant)
        return ant

    # -- per-tick colony-level dynamics ---------------------------------
    def _caste_probs(self):
        if self.cfg["caste_override"]:
            return self.cfg["caste_override"]
        pop = self.schedule.get_agent_count()
        probs = config.CASTE_CURVE[0][1]
        for threshold, p in config.CASTE_CURVE:
            if pop >= threshold:
                probs = p
        return probs

    def _population_of(self, colony_id):
        return sum(1 for a in self.schedule.agents if a.colony == colony_id)

    def _maybe_birth(self, colony_id):
        if self._population_of(colony_id) >= config.MAX_POPULATION:
            return
        chambers = [self.graph.nodes[n] for n in self.colony_by_id[colony_id]["fungus_nodes"]]
        avg_health = sum(c["health"] for c in chambers) / len(chambers)
        if avg_health < config.BIRTH_FUNGUS_SURPLUS_THRESHOLD:
            return
        boost = 1.0
        if self.cfg["founding_queens"] > 1 and self.tick < config.PLEOMETROSIS_WINDOW:
            boost = self.cfg["founding_queens"]
        if self.random.random() > min(0.95, config.BIRTH_CHANCE_PER_TICK * boost):
            return
        probs = self._caste_probs()
        castes, weights = zip(*probs.items())
        caste = self.random.choices(castes, weights=weights, k=1)[0]
        self._spawn_ant(caste, colony_id)
        cost_each = config.BIRTH_FUNGUS_COST / len(chambers)
        for c in chambers:
            c["health"] = max(0.0, c["health"] - cost_each)

    def _decay_pheromone(self):
        rate = self.cfg["pheromone_evaporation"]
        for u, v, data in self.graph.edges(data=True):
            if self.graph.nodes[u]["domain"] == "surface" or self.graph.nodes[v]["domain"] == "surface":
                data["pheromone"] = max(config.PHEROMONE_MIN, data["pheromone"] * rate)

    def _update_season(self):
        if not self.cfg["drought_enabled"]:
            self.season_multiplier = 1.0
            self.raining = False
            return
        phase = (self.tick % config.SEASON_LENGTH) / config.SEASON_LENGTH
        wet = 0.5 + 0.5 * math.sin(2 * math.pi * phase)
        lo, hi = config.DROUGHT_MIN_MULTIPLIER, config.DROUGHT_MAX_MULTIPLIER
        self.season_multiplier = lo + (hi - lo) * wet

        if self.raining:
            self._rain_ticks_left -= 1
            if self._rain_ticks_left <= 0:
                self.raining = False
        else:
            rain_chance = config.RAIN_CHANCE_PER_TICK * (0.4 + wet)
            if self.random.random() < rain_chance:
                self.raining = True
                self._rain_ticks_left = self.random.randint(*config.RAIN_DURATION)

    def _fungus_upkeep_and_disease(self):
        disease_on = self.cfg["disease_enabled"]
        tended_chambers = set()
        if disease_on:
            for a in self.schedule.agents:
                if a.task == "fungus_tend" and self.graph.nodes[a.node]["kind"] == "fungus":
                    tended_chambers.add(a.node)

        for c in self.colonies:
            chambers = [self.graph.nodes[n] for n in c["fungus_nodes"]]
            if disease_on:
                avg_infection = sum(ch.get("infection", 0.0) for ch in chambers) / len(chambers)
            for node_id, ch in zip(c["fungus_nodes"], chambers):
                ch["health"] = max(0.0, ch["health"] - config.FUNGUS_UPKEEP_PER_TICK)
                if disease_on:
                    infection = ch.get("infection", 0.0)
                    infection += config.DISEASE_GROWTH_RATE * infection * (1 - infection)
                    infection += (avg_infection - infection) * config.DISEASE_SPREAD_RATE
                    if node_id in tended_chambers:
                        infection = max(0.0, infection - config.DISEASE_HYGIENE_REDUCTION)
                    infection = max(0.0, min(1.0, infection))
                    ch["infection"] = infection
                    ch["health"] = max(0.0, ch["health"] - infection * config.DISEASE_DAMAGE_RATE)

    def _regrow_trees(self):
        for n in self.tree_nodes:
            d = self.graph.nodes[n]
            if d.get("dead"):
                continue
            if d["biomass"] < config.TREE_DEAD_THRESHOLD:
                d["depleted_ticks"] = d.get("depleted_ticks", 0) + 1
            else:
                d["depleted_ticks"] = 0
            if self.cfg["finite_trees"] and d["depleted_ticks"] >= config.TREE_DEATH_TICKS:
                d["dead"] = True
                d["biomass"] = 0.0
                continue
            d["biomass"] = min(
                config.TREE_MAX_BIOMASS,
                d["biomass"] + config.TREE_REGROWTH_PER_TICK * self.season_multiplier,
            )

    def step(self):
        self.schedule.step()
        self._decay_pheromone()
        self._update_season()
        self._fungus_upkeep_and_disease()
        self._regrow_trees()
        for c in self.colonies:
            self._maybe_birth(c["id"])
        self.tick += 1
        self._record_history()

    def _record_history(self):
        colonies_stats = {}
        for c in self.colonies:
            pop_by_caste = {"minim": 0, "minor": 0, "media": 0, "major": 0}
            for a in self.schedule.agents:
                if a.colony == c["id"]:
                    pop_by_caste[a.caste] += 1
            fungus_chambers = [self.graph.nodes[n] for n in c["fungus_nodes"]]
            avg_fungus = sum(ch["health"] for ch in fungus_chambers) / len(fungus_chambers)
            avg_infection = sum(ch.get("infection", 0.0) for ch in fungus_chambers) / len(fungus_chambers)
            colonies_stats[c["id"]] = {
                "population": dict(pop_by_caste),
                "total_population": sum(pop_by_caste.values()),
                "avg_fungus_health": round(avg_fungus, 2),
                "avg_infection": round(avg_infection, 3),
                "leaves_delivered": round(self.leaves_delivered[c["id"]], 2),
            }
        self.history.append(
            {
                "tick": self.tick,
                "colonies": colonies_stats,
                "season_multiplier": round(self.season_multiplier, 3),
                "raining": self.raining,
            }
        )
        if len(self.history) > 500:
            self.history = self.history[-500:]
