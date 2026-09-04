from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from simulation import ColonyModel
from simulation.scenario import SCENARIO_FIELDS, SWEEPABLE_FIELDS
from simulation.serialize import serialize_state
from simulation.sweep import run_sweep

app = FastAPI(title="Leafcutter Ant Colony Simulation")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_SWEEP_CELLS = 36
MAX_SWEEP_TICKS = 2000

_sims: Dict[str, ColonyModel] = {"default": ColonyModel(seed=None)}


def _get_sim(sim_id: str) -> ColonyModel:
    if sim_id not in _sims:
        raise HTTPException(404, f"no simulation with id '{sim_id}'")
    return _sims[sim_id]


class ResetRequest(BaseModel):
    seed: Optional[int] = None
    scenario: Optional[Dict[str, Any]] = None


@app.post("/api/simulation/reset")
def reset_simulation(req: Optional[ResetRequest] = None, sim_id: str = "default"):
    seed = req.seed if req else None
    scenario = req.scenario if req else None
    _sims[sim_id] = ColonyModel(seed=seed, scenario=scenario)
    return serialize_state(_sims[sim_id])


@app.get("/api/simulation/state")
def get_state(sim_id: str = "default"):
    return serialize_state(_get_sim(sim_id))


@app.post("/api/simulation/step")
def step_simulation(n: int = 1, sim_id: str = "default"):
    if n < 1 or n > 200:
        raise HTTPException(400, "n must be between 1 and 200")
    model = _get_sim(sim_id)
    for _ in range(n):
        model.step()
    return serialize_state(model)


@app.get("/api/simulation/history")
def get_history(sim_id: str = "default"):
    return _get_sim(sim_id).history


@app.delete("/api/simulation/{sim_id}")
def delete_simulation(sim_id: str):
    if sim_id == "default":
        raise HTTPException(400, "cannot delete the default simulation")
    _sims.pop(sim_id, None)
    return {"ok": True}


@app.get("/api/scenario/schema")
def scenario_schema():
    return {"fields": SCENARIO_FIELDS}


class SweepRequest(BaseModel):
    param_x: str
    x_values: List[Any]
    param_y: str
    y_values: List[Any]
    ticks: int = 600
    seed: int = 1
    base_scenario: Optional[Dict[str, Any]] = None


@app.post("/api/sweep")
def sweep(req: SweepRequest):
    if req.param_x not in SWEEPABLE_FIELDS or req.param_y not in SWEEPABLE_FIELDS:
        raise HTTPException(400, f"params must be one of {SWEEPABLE_FIELDS}")
    if req.param_x == req.param_y:
        raise HTTPException(400, "param_x and param_y must differ")
    cells = len(req.x_values) * len(req.y_values)
    if cells > MAX_SWEEP_CELLS:
        raise HTTPException(400, f"grid too large ({cells} cells, max {MAX_SWEEP_CELLS})")
    if req.ticks > MAX_SWEEP_TICKS:
        raise HTTPException(400, f"ticks too large (max {MAX_SWEEP_TICKS})")
    grid = run_sweep(
        req.param_x, req.x_values, req.param_y, req.y_values, req.ticks, req.seed, req.base_scenario
    )
    return {"param_x": req.param_x, "param_y": req.param_y, "grid": grid}


@app.get("/api/health")
def health():
    return {"status": "ok"}
