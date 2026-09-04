from . import config

# Describes every scenario field for the frontend so the controls panel and
# the sweep-experiment picker can be built generically instead of hardcoding
# each variant twice (once per side of the stack).
SCENARIO_FIELDS = [
    {
        "key": "founding_queens",
        "label": "Founding queens (pleometrosis)",
        "group": "Founding",
        "type": "number",
        "min": 1,
        "max": 5,
        "step": 1,
        "help": "More than one boosts early growth for a while, before reverting to single-queen rates.",
    },
    {
        "key": "pheromone_alpha",
        "label": "Trail bias (alpha)",
        "group": "Recruitment",
        "type": "number",
        "min": 0.2,
        "max": 5,
        "step": 0.2,
        "help": "How strongly ants prefer already-marked trails. Low = more exploration, high = fast lock-in.",
    },
    {
        "key": "exploration_floor",
        "label": "Exploration floor",
        "group": "Recruitment",
        "type": "number",
        "min": 0.0,
        "max": 0.5,
        "step": 0.01,
        "help": "Baseline chance an ant samples an unmarked/weak trail instead of following pheromone.",
    },
    {
        "key": "pheromone_evaporation",
        "label": "Pheromone persistence",
        "group": "Recruitment",
        "type": "number",
        "min": 0.9,
        "max": 0.999,
        "step": 0.001,
        "help": "Multiplicative decay applied to trail pheromone each tick - higher means trails last longer.",
    },
    {
        "key": "caste_override",
        "label": "Caste ratio override",
        "group": "Division of labor",
        "type": "caste_ratio",
        "help": "Pin the worker caste mix instead of letting it follow the population-based default curve.",
    },
    {
        "key": "num_leaf_trees",
        "label": "Leaf-source trees",
        "group": "Resources",
        "type": "number",
        "min": 3,
        "max": 16,
        "step": 1,
    },
    {
        "key": "tree_layout",
        "label": "Tree distribution",
        "group": "Resources",
        "type": "select",
        "options": ["scattered", "patchy"],
        "help": "Patchy clusters trees into a few dense groves instead of scattering them evenly.",
    },
    {
        "key": "chemical_defense",
        "label": "Plant chemical defense",
        "group": "Resources",
        "type": "bool",
        "help": "Some trees reject cutting attempts - ants waste trips on unproductive trees until trails redirect.",
    },
    {
        "key": "finite_trees",
        "label": "Finite trees",
        "group": "Resources",
        "type": "bool",
        "help": "A tree exhausted for too long dies permanently instead of always regrowing.",
    },
    {
        "key": "disease_enabled",
        "label": "Escovopsis (garden disease)",
        "group": "Threats",
        "type": "bool",
        "help": "A parasitic fungus that attacks the garden. Hygiene from fungus-tending ants can suppress it - or not.",
    },
    {
        "key": "phorid_flies_enabled",
        "label": "Phorid fly parasitism",
        "group": "Threats",
        "type": "bool",
        "help": "Foragers without a minim escort (probabilistic, based on the colony's minim:media ratio) cut less per trip.",
    },
    {
        "key": "drought_enabled",
        "label": "Seasonal drought + rain",
        "group": "Threats",
        "type": "bool",
        "help": "Tree regrowth cycles with a wet/dry season, and rain events pause outdoor foraging.",
    },
    {
        "key": "rival_colony",
        "label": "Rival colony",
        "group": "Competition",
        "type": "bool",
        "help": "A second colony contests trees near the midpoint between the two nests.",
    },
]

for _f in SCENARIO_FIELDS:
    _f["default"] = config.DEFAULT_SCENARIO[_f["key"]]

SWEEPABLE_FIELDS = [
    f["key"] for f in SCENARIO_FIELDS if f["type"] in ("number", "bool", "select")
]


def make_scenario(overrides=None):
    """Merge a partial overrides dict over DEFAULT_SCENARIO, ignoring unknown keys."""
    cfg = dict(config.DEFAULT_SCENARIO)
    if overrides:
        for k, v in overrides.items():
            if k in cfg and v is not None:
                cfg[k] = v
    return cfg
