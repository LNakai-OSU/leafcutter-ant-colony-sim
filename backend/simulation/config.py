"""
Tunable parameters for the colony simulation.

Qualitative structure (caste roles, fungus mutualism, trail-pheromone
recruitment, waste chambers kept apart from fungus chambers, claustral
founding by a single queen) follows the general biology of leafcutter ants
(genus Atta / Acromyrmex) as described in Holldobler & Wilson, "The
Leafcutter Ants: Civilization by Instinct" (2010) and Wilson's earlier work
on caste and division of labor in Atta (1980).

The specific numbers below (decay rates, growth rates, caste-ratio curve)
are NOT measured literature values - real colonies run into the millions
of workers, which isn't renderable or simulatable in a browser at
interactive speed. They're illustrative parameters chosen to reproduce the
right qualitative dynamics (trail formation via reinforcement, caste ratio
shifting as the colony matures, fungus garden as the growth-limiting
resource) at a scale of dozens to a few hundred ants.
"""

# --- Nest structure ---
NUM_FUNGUS_CHAMBERS = 6
NUM_NURSERY_CHAMBERS = 3
NUM_WASTE_CHAMBERS = 2
NUM_JUNCTION_CHAMBERS = 4  # empty tunnel-junction chambers, no special role

# --- Foraging trail structure ---
NUM_TRUNK_JUNCTIONS = 3   # branch points between the entrance and the trees
NUM_LEAF_TREES = 8
TREE_MIN_RADIUS = 14.0    # trees are scattered this far from the entrance...
TREE_MAX_RADIUS = 34.0    # ...out to this far (units are arbitrary "meters")

TREE_MAX_BIOMASS = 100.0
TREE_REGROWTH_PER_TICK = 0.6
LEAF_CUT_AMOUNT = {
    # how much biomass a single ant of this caste cuts per visit
    "media": 6.0,
    "minor": 2.0,
}

# --- Pheromone trail dynamics (ant-colony-optimization-style) ---
PHEROMONE_EVAPORATION = 0.985  # multiplicative decay applied each tick
PHEROMONE_DEPOSIT_SCALE = 0.35  # deposit = load * quality * this
PHEROMONE_MIN = 0.01
PHEROMONE_ALPHA = 2.0  # exponent biasing edge choice toward stronger trails
EXPLORATION_FLOOR = 0.05  # ants still explore weak/unmarked edges sometimes

# --- Movement ---
EDGE_SPEED = {
    # fraction of an edge crossed per tick, by caste (bigger ants ~ faster)
    "minim": 0.34,
    "minor": 0.4,
    "media": 0.32,
    "major": 0.28,
}

# --- Fungus garden / colony growth ---
FUNGUS_MAX_HEALTH = 100.0
FUNGUS_FEED_PER_LEAF_UNIT = 2.2   # fungus health gained per unit of leaf delivered
FUNGUS_UPKEEP_PER_TICK = 0.05     # fungus health lost per tick per chamber
BIRTH_FUNGUS_SURPLUS_THRESHOLD = 45.0  # avg fungus health needed to rear brood
BIRTH_FUNGUS_COST = 5.0           # fungus health consumed per new ant reared
BIRTH_CHANCE_PER_TICK = 0.35      # chance a birth is attempted when above threshold
MAX_POPULATION = 400              # rendering/perf cap, not a biological limit

# --- Caste ratio as the colony matures (population-based, not age-based -
# a simplification of real temporal + size polyethism) ---
# (population_threshold, {caste: probability})
CASTE_CURVE = [
    (0, {"minim": 0.7, "minor": 0.2, "media": 0.1, "major": 0.0}),
    (20, {"minim": 0.45, "minor": 0.25, "media": 0.25, "major": 0.05}),
    (60, {"minim": 0.3, "minor": 0.25, "media": 0.35, "major": 0.1}),
    (150, {"minim": 0.2, "minor": 0.2, "media": 0.45, "major": 0.15}),
]

STARTING_COLONY = {"minim": 6, "minor": 2, "media": 2, "major": 0}

CASTE_SIZE = {"minim": 0.35, "minor": 0.55, "media": 0.8, "major": 1.15}
