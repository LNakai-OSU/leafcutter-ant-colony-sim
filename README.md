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
model itself runs at several thousand ticks/second - the speed control is
about watch-ability, not simulation performance).

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
network uses the pheromone-biased random walk. Trees regrow at a fixed
rate and ants don't die in this version - population is capped only by the
rendering/perf ceiling and by how much the fungus garden can support.

## API

| Endpoint | What it does |
|---|---|
| `GET /api/simulation/state` | Full current state: graph nodes/edges, every ant, latest stats |
| `POST /api/simulation/step?n=1` | Advance the model `n` ticks (1-200), return the new state |
| `POST /api/simulation/reset` | Start a fresh colony (optional `{"seed": 123}` body) |
| `GET /api/simulation/history` | Time series of population/fungus/foraging stats |

The frontend drives the simulation itself by polling `/step` on an
interval - there's no background thread advancing ticks on its own, so the
simulation is fully paused whenever nothing is polling it.
