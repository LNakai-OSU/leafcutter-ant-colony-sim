import { Fragment, useMemo, useState } from "react";
import { runSweep } from "../api";

const METRICS = [
  { key: "total_population", label: "Final population" },
  { key: "avg_fungus_health", label: "Avg. fungus health" },
  { key: "avg_infection", label: "Avg. infection" },
  { key: "leaves_delivered", label: "Leaves delivered" },
];

function defaultValues(field) {
  if (field.type === "bool") return [false, true];
  if (field.type === "select") return field.options;
  const steps = 4;
  const vals = [];
  for (let i = 0; i < steps; i++) {
    const raw = field.min + (field.max - field.min) * (i / (steps - 1));
    vals.push(Math.round(raw / field.step) * field.step);
  }
  return [...new Set(vals.map((v) => Number(v.toFixed(4))))];
}

function cellStyle(value, min, max) {
  const t = max > min ? (value - min) / (max - min) : 0.5;
  const lo = [34, 28, 20];
  const hi = [224, 168, 60];
  const rgb = lo.map((l, i) => Math.round(l + (hi[i] - l) * t));
  return {
    background: `rgb(${rgb.join(",")})`,
    color: t < 0.45 ? "#f2ede2" : "#1a1610",
  };
}

export default function SweepView({ schema }) {
  const sweepable = useMemo(() => schema.fields.filter((f) => ["number", "bool", "select"].includes(f.type)), [schema]);
  const [xKey, setXKey] = useState(sweepable[0].key);
  const [yKey, setYKey] = useState(sweepable[1].key);
  const [ticks, setTicks] = useState(600);
  const [seed, setSeed] = useState(1);
  const [metric, setMetric] = useState("total_population");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const xField = sweepable.find((f) => f.key === xKey);
  const yField = sweepable.find((f) => f.key === yKey);

  const run = () => {
    if (xKey === yKey) {
      setError("Pick two different parameters.");
      return;
    }
    setLoading(true);
    setError(null);
    runSweep({
      param_x: xKey,
      x_values: defaultValues(xField),
      param_y: yKey,
      y_values: defaultValues(yField),
      ticks,
      seed,
    })
      .then((r) => setResult(r))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  };

  const flatValues = result ? result.grid.flat().map((c) => c[metric]) : [];
  const min = flatValues.length ? Math.min(...flatValues) : 0;
  const max = flatValues.length ? Math.max(...flatValues) : 1;

  return (
    <div className="sweep-view">
      <p className="muted ab-intro">
        Batch-runs the headless simulation across a grid of two parameters (no rendering - this
        reuses the same model that drives the live view) and reports the final outcome for each
        combination. Good for finding thresholds - e.g. the trail-bias/exploration-floor
        trade-off, or how much drought a colony can tolerate.
      </p>

      {error && <div className="error-banner">{error}</div>}

      <div className="sweep-controls">
        <label className="field">
          <span>X axis</span>
          <select value={xKey} onChange={(e) => setXKey(e.target.value)}>
            {sweepable.map((f) => (
              <option key={f.key} value={f.key}>
                {f.label}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Y axis</span>
          <select value={yKey} onChange={(e) => setYKey(e.target.value)}>
            {sweepable.map((f) => (
              <option key={f.key} value={f.key}>
                {f.label}
              </option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Ticks per run</span>
          <input type="number" className="mono" value={ticks} min={100} max={2000} step={100} onChange={(e) => setTicks(Number(e.target.value))} />
        </label>
        <label className="field">
          <span>Seed</span>
          <input type="number" className="mono" value={seed} onChange={(e) => setSeed(Number(e.target.value))} />
        </label>
        <label className="field">
          <span>Color by</span>
          <select value={metric} onChange={(e) => setMetric(e.target.value)}>
            {METRICS.map((m) => (
              <option key={m.key} value={m.key}>
                {m.label}
              </option>
            ))}
          </select>
        </label>
        <button className="btn btn-primary" onClick={run} disabled={loading}>
          {loading ? "Running..." : "Run sweep"}
        </button>
      </div>

      {result && (
        <div className="heatmap-wrap">
          <div className="heatmap" style={{ gridTemplateColumns: `auto repeat(${result.grid.length}, 1fr)` }}>
            <div className="heatmap-corner mono">{yField.label} \ {xField.label}</div>
            {result.grid.map((row, xi) => (
              <div className="heatmap-col-label mono" key={`xl-${xi}`}>
                {String(row[0].x)}
              </div>
            ))}
            {result.grid[0].map((_, yi) => (
              <Fragment key={`row-${yi}`}>
                <div className="heatmap-row-label mono">{String(result.grid[0][yi].y)}</div>
                {result.grid.map((row, xi) => {
                  const cell = row[yi];
                  const value = cell[metric];
                  return (
                    <div
                      key={`c-${xi}-${yi}`}
                      className="heatmap-cell mono"
                      style={cellStyle(value, min, max)}
                      title={`${xField.label}=${cell.x}, ${yField.label}=${cell.y}`}
                    >
                      {typeof value === "number" ? value.toFixed(1) : String(value)}
                    </div>
                  );
                })}
              </Fragment>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
