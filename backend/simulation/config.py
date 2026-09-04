"""
Fixed structural constants + the default scenario for the colony
simulation. See README for the biology this is modeling and which numbers
are real vs illustrative.

`DEFAULT_SCENARIO` holds everything a caller can override per-simulation
(see `scenario.py`); everything else here is nest/graph structure that
doesn't vary between scenarios.
"""

# --- Fixed nest structure ---
NUM_FUNGUS_CHAMBERS = 6
NUM_NURSERY_CHAMBERS = 3
NUM_WASTE_CHAMBERS = 2
NUM_JUNCTION_CHAMBERS = 4
NUM_TRUNK_JUNCTIONS = 3

TREE_MIN_RADIUS = 14.0
TREE_MAX_RADIUS = 34.0
TREE_MAX_BIOMASS = 100.0
TREE_REGROWTH_PER_TICK = 0.6

LEAF_CUT_AMOUNT = {"media": 6.0, "minor": 2.0}
PHEROMONE_MIN = 0.01
PHEROMONE_DEPOSIT_SCALE = 0.35

EDGE_SPEED = {"minim": 0.34, "minor": 0.4, "media": 0.32, "major": 0.28}

FUNGUS_MAX_HEALTH = 100.0
FUNGUS_FEED_PER_LEAF_UNIT = 2.2
FUNGUS_UPKEEP_PER_TICK = 0.05
BIRTH_FUNGUS_SURPLUS_THRESHOLD = 45.0
BIRTH_FUNGUS_COST = 5.0
BIRTH_CHANCE_PER_TICK = 0.35
MAX_POPULATION = 400  # rendering/perf cap, not a biological limit

# (population_threshold, {caste: probability}) - population-based stand-in
# for real temporal + size polyethism (young colonies skew minim-heavy)
CASTE_CURVE = [
    (0, {"minim": 0.7, "minor": 0.2, "media": 0.1, "major": 0.0}),
    (20, {"minim": 0.45, "minor": 0.25, "media": 0.25, "major": 0.05}),
    (60, {"minim": 0.3, "minor": 0.25, "media": 0.35, "major": 0.1}),
    (150, {"minim": 0.2, "minor": 0.2, "media": 0.45, "major": 0.15}),
]

STARTING_COLONY = {"minim": 6, "minor": 2, "media": 2, "major": 0}
CASTE_SIZE = {"minim": 0.35, "minor": 0.55, "media": 0.8, "major": 1.15}

# --- Threat / variant tuning (only active when the scenario flag is set) ---
DISEASE_GROWTH_RATE = 0.06        # logistic growth rate of untreated infection
DISEASE_SPREAD_RATE = 0.04        # diffusion between adjacent fungus chambers
DISEASE_DAMAGE_RATE = 1.2         # extra health loss per tick, scaled by infection level
DISEASE_HYGIENE_REDUCTION = 0.006 # infection removed per fungus-tend visit (many tenders still add up)

PHORID_YIELD_PENALTY = 0.45       # cut-amount multiplier on an un-escorted trip

SEASON_LENGTH = 500                # ticks per full wet/dry cycle
DROUGHT_MIN_MULTIPLIER = 0.25
DROUGHT_MAX_MULTIPLIER = 1.4
RAIN_CHANCE_PER_TICK = 0.02
RAIN_DURATION = (5, 15)

TREE_DEAD_THRESHOLD = 1.5
TREE_DEATH_TICKS = 60               # consecutive ticks below threshold before permanent death

PATCH_CLUSTER_COUNT = 3
PATCH_JITTER_DEG = 18

RIVAL_OFFSET = 20.0                  # distance between the two colonies' entrances
CONTESTED_RADIUS = 20.0              # a tree within this range of a trunk cluster connects to it

PLEOMETROSIS_WINDOW = 150            # ticks the multi-queen founding boost lasts

# --- Default scenario: every field here can be overridden per-simulation ---
DEFAULT_SCENARIO = {
    "founding_queens": 1,           # pleometrosis: >1 cooperating queens boosts early growth
    "pheromone_alpha": 2.0,         # exponent biasing trail choice toward stronger trails
    "exploration_floor": 0.05,      # chance ants still sample weak/unmarked trails
    "pheromone_evaporation": 0.985, # multiplicative decay applied each tick
    "caste_override": None,         # fixed {caste: prob} dict, or None to use CASTE_CURVE
    "num_leaf_trees": 8,
    "tree_layout": "scattered",     # "scattered" | "patchy"
    "chemical_defense": False,      # trees can reject a cutting attempt
    "finite_trees": False,          # trees can be permanently exhausted
    "disease_enabled": False,       # Escovopsis-style fungus garden pathogen
    "phorid_flies_enabled": False,  # media foraging efficiency drops without a minim escort
    "drought_enabled": False,       # seasonal regrowth cycle + rain pauses on foraging
    "rival_colony": False,          # a second colony contesting the same trees
}
