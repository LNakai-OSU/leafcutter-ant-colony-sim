const BASE = "http://localhost:8010";

async function req(path, options) {
  const res = await fetch(`${BASE}${path}`, options);
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`${path} failed: ${res.status} ${body}`);
  }
  return res.json();
}

export function getState(simId = "default") {
  return req(`/api/simulation/state?sim_id=${simId}`);
}

export function stepSimulation(n = 1, simId = "default") {
  return req(`/api/simulation/step?n=${n}&sim_id=${simId}`, { method: "POST" });
}

export function resetSimulation(scenario, seed, simId = "default") {
  return req(`/api/simulation/reset?sim_id=${simId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ seed: seed ?? null, scenario: scenario ?? null }),
  });
}

export function deleteSimulation(simId) {
  return req(`/api/simulation/${simId}`, { method: "DELETE" });
}

export function getHistory(simId = "default") {
  return req(`/api/simulation/history?sim_id=${simId}`);
}

export function getScenarioSchema() {
  return req("/api/scenario/schema");
}

export function runSweep(body) {
  return req("/api/sweep", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}
