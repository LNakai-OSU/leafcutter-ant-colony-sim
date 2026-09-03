const BASE = "http://localhost:8010";

async function req(path, options) {
  const res = await fetch(`${BASE}${path}`, options);
  if (!res.ok) {
    throw new Error(`${path} failed: ${res.status}`);
  }
  return res.json();
}

export function getState() {
  return req("/api/simulation/state");
}

export function stepSimulation(n = 1) {
  return req(`/api/simulation/step?n=${n}`, { method: "POST" });
}

export function resetSimulation(seed) {
  return req("/api/simulation/reset", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(seed != null ? { seed } : {}),
  });
}

export function getHistory() {
  return req("/api/simulation/history");
}
