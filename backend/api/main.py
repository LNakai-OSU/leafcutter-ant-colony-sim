from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from simulation import ColonyModel
from simulation.serialize import serialize_state

app = FastAPI(title="Leafcutter Ant Colony Simulation")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)

_state = {"model": ColonyModel(seed=None)}


class ResetRequest(BaseModel):
    seed: Optional[int] = None


@app.post("/api/simulation/reset")
def reset_simulation(req: Optional[ResetRequest] = None):
    seed = req.seed if req else None
    _state["model"] = ColonyModel(seed=seed)
    return serialize_state(_state["model"])


@app.get("/api/simulation/state")
def get_state():
    return serialize_state(_state["model"])


@app.post("/api/simulation/step")
def step_simulation(n: int = 1):
    if n < 1 or n > 200:
        raise HTTPException(400, "n must be between 1 and 200")
    model = _state["model"]
    for _ in range(n):
        model.step()
    return serialize_state(model)


@app.get("/api/simulation/history")
def get_history():
    return _state["model"].history


@app.get("/api/health")
def health():
    return {"status": "ok"}
