import { useEffect, useRef, useState } from "react";
import ColonyGraph3D from "./ColonyGraph3D";
import StatsPanel from "./StatsPanel";
import ScenarioPanel from "./ScenarioPanel";
import { resetSimulation, stepSimulation } from "../api";
import { defaultsFromSchema } from "../scenarioDefaults";

const POLL_MS = 400;
const SIM_A = "ab_a";
const SIM_B = "ab_b";

export default function ABCompare({ schema }) {
  const [scenarioA, setScenarioA] = useState(() => defaultsFromSchema(schema));
  const [scenarioB, setScenarioB] = useState(() => ({ ...defaultsFromSchema(schema), disease_enabled: true }));
  const [seed, setSeed] = useState(1);
  const [stateA, setStateA] = useState(null);
  const [stateB, setStateB] = useState(null);
  const [historyA, setHistoryA] = useState([]);
  const [historyB, setHistoryB] = useState([]);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(5);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);
  const startedRef = useRef(false);

  const start = () => {
    setPlaying(false);
    setHistoryA([]);
    setHistoryB([]);
    setError(null);
    Promise.all([resetSimulation(scenarioA, seed, SIM_A), resetSimulation(scenarioB, seed, SIM_B)])
      .then(([a, b]) => {
        setStateA(a);
        setStateB(b);
        if (a.stats) setHistoryA([a.stats]);
        if (b.stats) setHistoryB([b.stats]);
      })
      .catch((e) => setError(e.message));
  };

  useEffect(() => {
    if (!startedRef.current) {
      startedRef.current = true;
      start();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!playing) {
      clearInterval(intervalRef.current);
      return;
    }
    intervalRef.current = setInterval(() => {
      Promise.all([stepSimulation(speed, SIM_A), stepSimulation(speed, SIM_B)])
        .then(([a, b]) => {
          setStateA(a);
          setStateB(b);
          if (a.stats) setHistoryA((h) => [...h, a.stats].slice(-500));
          if (b.stats) setHistoryB((h) => [...h, b.stats].slice(-500));
        })
        .catch((e) => {
          setError(e.message);
          setPlaying(false);
        });
    }, POLL_MS);
    return () => clearInterval(intervalRef.current);
  }, [playing, speed]);

  const combinedHistory = historyA.map((hA, i) => {
    const hB = historyB[i];
    return {
      tick: hA.tick,
      season_multiplier: hA.season_multiplier,
      raining: hA.raining,
      colonies: {
        A: hA.colonies.A,
        ...(hB ? { B: hB.colonies.A } : {}),
      },
    };
  });

  return (
    <div className="ab-compare">
      <p className="muted ab-intro">
        Run two colonies from the same seed with one (or more) settings different, side by
        side. Good for answering "does X actually help or hurt" instead of eyeballing a
        single run.
      </p>

      {error && <div className="error-banner">{error}</div>}

      <div className="ab-setup-row">
        <label className="field">
          <span>Shared seed</span>
          <input
            type="number"
            className="mono"
            value={seed}
            onChange={(e) => setSeed(Number(e.target.value))}
          />
        </label>
        <button className="btn btn-primary" onClick={start}>
          Reset &amp; start both
        </button>
        <button className="btn btn-ghost" onClick={() => setPlaying((p) => !p)} disabled={!stateA}>
          {playing ? "Pause" : "Play"}
        </button>
        {[1, 3, 8, 20].map((s) => (
          <button
            key={s}
            className={`chip-btn ${speed === s ? "chip-btn-active" : ""}`}
            onClick={() => setSpeed(s)}
          >
            {s}x
          </button>
        ))}
      </div>

      <div className="ab-grid">
        <div className="ab-column">
          <h3 className="ab-column-title">Colony A</h3>
          <ScenarioPanel schema={schema.fields} scenario={scenarioA} onChange={setScenarioA} onApply={start} applyLabel="Apply & restart both" />
          {stateA && (
            <ColonyGraph3D
              nodes={stateA.nodes}
              edges={stateA.edges}
              ants={stateA.ants}
              raining={stateA.raining}
              rivalColony={scenarioA.rival_colony}
            />
          )}
        </div>
        <div className="ab-column">
          <h3 className="ab-column-title">Colony B</h3>
          <ScenarioPanel schema={schema.fields} scenario={scenarioB} onChange={setScenarioB} onApply={start} applyLabel="Apply & restart both" />
          {stateB && (
            <ColonyGraph3D
              nodes={stateB.nodes}
              edges={stateB.edges}
              ants={stateB.ants}
              raining={stateB.raining}
              rivalColony={scenarioB.rival_colony}
            />
          )}
        </div>
      </div>

      {combinedHistory.length > 0 && (
        <StatsPanel
          history={combinedHistory}
          colonyIds={["A", "B"]}
          showInfection={scenarioA.disease_enabled || scenarioB.disease_enabled}
          showSeason={false}
        />
      )}
    </div>
  );
}
