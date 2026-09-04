# Leafcutter Ant Colony Simulation

An agent-based simulation of a leafcutter ant colony (genus *Atta*/
*Acromyrmex*) - caste division of labor, fungus-garden agriculture, and
pheromone-trail foraging - rendered live as a 3D colored graph.

- `backend/` - Python. `simulation/` is a [Mesa](https://mesa.readthedocs.io/)
  agent-based model; `api/` is a thin FastAPI wrapper that steps the model
  and serves its state as JSON.
- `frontend/` - React + Vite + [react-three-fiber](https://docs.pmnd.rs/react-three-fiber)
  (Three.js) for the 3D graph, [recharts](https://recharts.org/) for the
  population/fungus/foraging time series.

## Running it

```bash
# Terminal 1 - backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8010

# Terminal 2 - frontend
cd frontend
npm install
npm run dev   # http://localhost:5173
```

Hit Play. Speed controls how many simulation ticks run per UI refresh (the
model itself runs at several hundred to several thousand ticks/second
depending on population - the speed control is about watch-ability, not
simulation performance). Three tabs:

- **Colony** - the live 3D view, with a "Scenario settings" panel exposing
  every variant below. Changing a setting takes effect on the next "New
  colony".
- **Compare A/B** - two independently-configured colonies started from the
  same seed, run side by side with combined stats charts, so you can
  actually answer "does this variant help or hurt" instead of eyeballing
  one run.
- **Experiments** - batch-runs the headless model (no rendering) across a
  grid of two parameters and reports the outcome as a heatmap - e.g. how
  final population depends on trail-bias vs. exploration-floor.

## The biology this is modeling

The qualitative structure follows the general biology described in
Holldobler & Wilson's *The Leafcutter Ants: Civilization by Instinct*
(2010) and E.O. Wilson's earlier work on caste and division of labor in
*Atta* (1980):

- **Fungus mutualism.** Leafcutter ants don't eat leaves - they cut them,
  carry them home, and feed them to a cultivated fungus (*Leucoagaricus*)
  that is the colony's actual food source. The fungus garden is the
  resource that limits colony growth in this model, exactly as it does in
  the real system.
- **Caste polymorphism.** Workers come in discrete size classes with
  different jobs: **minims** (smallest) tend the brood and the fungus
  garden and rarely leave the nest; **minors** handle waste and back up
  fungus tending; **mediae** are the primary leaf-cutting foragers; **majors**
  (largest) mostly hold position near the nest entrance and trunk trails -
  a simplified stand-in for their real role in colony defense and clearing
  trail obstructions.
- **Trail pheromone recruitment.** Successful foragers reinforce the route
  back to a productive tree by depositing pheromone as they return; unused
  trails evaporate. This is the same reinforcement dynamic that real Atta
  trails show (and that inspired Ant Colony Optimization in computer
  science) - a colony's trail network is a live record of where foraging
  has recently paid off, not a fixed map.
- **Nest layout.** Waste chambers are deliberately placed apart from the
  fungus-garden cluster - real Atta colonies keep refuse away from the
  gardens. Nursery chambers cluster near the queen. Trails branch from a
  single nest entrance out to multiple leaf-source trees, mirroring the
  trunk-and-branch trail systems Atta colonies cut through the understory,
  sometimes extending well over a hundred meters from the nest.
- **Colony maturation.** A young colony (founded by a single queen who
  seals herself in a chamber - "claustral" founding) is dominated by
  minims; a mature colony has proportionally more mediae and majors. This
  model approximates that with a population-based caste-ratio curve
  (`simulation/config.py: CASTE_CURVE`) rather than modeling queen founding
  or individual ant age directly.

## Scenario variants

Every field below lives in `simulation/config.py: DEFAULT_SCENARIO` and
`simulation/scenario.py: SCENARIO_FIELDS` (the latter is what the frontend's
scenario panel and the Experiments sweep picker are generated from - the UI
never hardcodes the variant list, it reads it from `GET /api/scenario/schema`).
A `ColonyModel(seed=..., scenario={...})` merges any subset of these over
the defaults, so every variant below composes with every other one.

**Founding**
- **Pleometrosis (founding queens)** - some Atta colonies found with
  multiple cooperating queens instead of one. Modeled as a starting-population
  multiplier plus a temporary birth-rate boost for the first
  `PLEOMETROSIS_WINDOW` ticks, not as literally simulating a queen-elimination
  fight (real pleometrosis ends with only one queen surviving).

**Recruitment** (the ant-colony-optimization-style trail mechanics)
- **Trail bias (alpha)** - how strongly ants prefer already-marked trails
  when choosing the next hop.
- **Exploration floor** - baseline chance of ignoring pheromone and sampling
  a trail anyway. Together with alpha this is a direct, adjustable
  explore/exploit knob - the **Experiments** tab is built to sweep exactly
  this pair.
- **Pheromone persistence** - the evaporation rate; higher means trails
  outlive the trip that made them.

**Division of labor**
- **Caste ratio override** - pins the worker-caste mix instead of letting it
  follow the population-based default curve, so you can directly test e.g.
  "what if this colony over-invests in majors."

**Resources**
- **Tree count / distribution** - "patchy" clusters trees into a few dense
  groves instead of scattering them evenly, producing a visibly different
  trail-network topology (a few thick trunk trails vs. many thin ones).
- **Plant chemical defense** - some trees get an `acceptance` roll; a
  rejected cutting attempt yields nothing, so unreliable trees simply never
  get reinforced rather than needing an explicit "avoid this tree" rule.
- **Finite trees** - a tree that stays depleted for `TREE_DEATH_TICKS` in a
  row dies permanently instead of always regrowing.

**Threats**
- **Escovopsis (garden disease)** - a real parasitic fungus that attacks
  Atta's cultivated garden. Modeled as per-chamber infection with logistic
  growth, diffusion between a colony's own chambers, and a flat hygiene
  suppression applied whenever a fungus-tending ant is present. The chosen
  growth/hygiene rates land the system right at a **bistable tipping
  point** - most runs suppress an introduced infection back to zero, but a
  real fraction of seeds spiral into full-blown infection and colony
  collapse, with no change to any setting. That's not a bug: it's the model
  showing that a young colony's fate can hinge on early, essentially
  random, staffing luck - run the same scenario across a few seeds in the
  **Experiments** tab to see the split.
- **Phorid fly parasitism** - real phorid flies target mediae specifically
  while they cut, and minims are known to ride the leaf fragments home
  specifically to fend them off. Rather than modeling literal escort-pairing
  between agents, an un-escorted trip is sampled probabilistically from the
  colony's current minim:media ratio - more minims per active forager means
  a better chance any given trip was escorted.
- **Seasonal drought + rain** - tree regrowth follows a sine-wave wet/dry
  cycle (`SEASON_LENGTH` ticks per cycle); rain events (more likely near the
  wet-season peak) pause outdoor movement on surface trail edges for a few
  ticks, without touching indoor nest activity.

**Competition**
- **Rival colony** - a second full nest is built at an offset, and trees
  near the midpoint get a trail edge to *both* colonies' nearest trunk
  instead of just one - a shared, contested resource, while trees closer to
  one side stay effectively exclusive to it. No special competition
  mechanic is needed beyond that: both colonies' foragers just draw from the
  same finite `tree.biomass` pool using the same rules they'd use alone.

## What's a real measurement vs. an illustrative simplification

Real Atta colonies run into the **millions** of workers and aren't
renderable or simulatable at interactive speed in a browser. Everything
here is deliberately scaled down to a few hundred agents (`MAX_POPULATION`
in `config.py`) - enough to show the right qualitative dynamics (trail
formation, caste-ratio shift, fungus-limited growth, eventual leveling-off
as local trees get depleted) without pretending to be a literature-accurate
population model. Specific numeric parameters - pheromone evaporation rate,
fungus upkeep cost, birth thresholds, leaf-cut amounts per caste - are
tuned by hand to produce watchable, stable dynamics, **not** copied from a
measured source. Where the model states a caste's *role* (what job it does)
that's grounded in the literature above; where it states a *rate or number*
that's a simplification made explicit here rather than dressed up as
research data.

Ant movement inside the nest uses shortest-path routing (an ant "knows its
way home" through familiar tunnels); only the outdoor foraging trail
network uses the pheromone-biased random walk. Ants themselves don't die in
this version (disease and drought act only on the fungus garden and
foraging efficiency, never directly on an ant) - population is capped only
by the rendering/perf ceiling (`MAX_POPULATION`) and by how much the fungus
garden can support. Trees regrow at a fixed seasonal rate unless `finite_trees`
is on, in which case a tree exhausted for too long dies for good.

## API

The backend holds any number of named simulation instances in memory
(`sim_id` query param, default `"default"`) - this is what lets the
Compare A/B tab run two independent colonies concurrently.

| Endpoint | What it does |
|---|---|
| `GET /api/simulation/state?sim_id=default` | Full current state: graph nodes/edges, every ant, latest stats, active scenario |
| `POST /api/simulation/step?n=1&sim_id=default` | Advance the model `n` ticks (1-200), return the new state |
| `POST /api/simulation/reset?sim_id=default` | Start a fresh colony (`{"seed": 123, "scenario": {...}}` body, both optional) |
| `DELETE /api/simulation/{sim_id}` | Drop a named instance (not the default one) |
| `GET /api/simulation/history?sim_id=default` | Time series of population/fungus/foraging stats |
| `GET /api/scenario/schema` | Every scenario field's type/range/label/help text - what the frontend renders its controls from |
| `POST /api/sweep` | Headless batch run across a 2D parameter grid (`param_x`, `x_values`, `param_y`, `y_values`, `ticks`, `seed`) - capped at 36 cells / 2000 ticks per run to keep it a synchronous request |

The frontend drives each simulation itself by polling `/step` on an
interval - there's no background thread advancing ticks on its own, so any
given simulation is fully paused whenever nothing is polling it. `/sweep`
is the exception: it runs its whole grid to completion inside the request
using the same `ColonyModel`, just without ever calling into the
frontend-facing endpoints.
