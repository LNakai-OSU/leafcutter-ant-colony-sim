import { useCallback, useEffect, useRef, useState } from "react";
import ColonyGraph3D from "./components/ColonyGraph3D";
import Controls from "./components/Controls";
import StatsPanel from "./components/StatsPanel";
import Legend from "./components/Legend";
import ScenarioPanel from "./components/ScenarioPanel";
import ABCompare from "./components/ABCompare";
import SweepView from "./components/SweepView";
import { getState, stepSimulation, resetSimulation, getScenarioSchema } from "./api";
import { defaultsFromSchema } from "./scenarioDefaults";
import "./App.css";

const POLL_MS = 350;
const TABS = [
  { id: "colony", label: "Colony" },
  { id: "compare", label: "Compare A/B" },
  { id: "experiments", label: "Experiments" },
];

function ColonyView({ schema }) {
  const [scenario, setScenario] = useState(() => defaultsFromSchema(schema));
  const [showScenario, setShowScenario] = useState(false);
  const [state, setState] = useState(null);
  const [history, setHistory] = useState([]);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(3);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);

  const applyState = useCallback((s) => {
    setState(s);
    if (s.stats) {
      setHistory((h) => [...h, s.stats].slice(-500));
    }
  }, []);

  useEffect(() => {
    getState()
      .then(applyState)
      .catch((e) => setError(e.message));
  }, [applyState]);

  useEffect(() => {
    if (!playing) {
      clearInterval(intervalRef.current);
      return;
    }
    intervalRef.current = setInterval(() => {
      stepSimulation(speed)
        .then(applyState)
        .catch((e) => {
          setError(e.message);
          setPlaying(false);
        });
    }, POLL_MS);
    return () => clearInterval(intervalRef.current);
  }, [playing, speed, applyState]);

  const handleStep = () => stepSimulation(1).then(applyState).catch((e) => setError(e.message));

  const handleReset = () => {
    setPlaying(false);
    setHistory([]);
    resetSimulation(scenario).then(applyState).catch((e) => setError(e.message));
  };

  return (
    <>
      {error && <div className="error-banner">{error}. Is the backend running on port 8010?</div>}

      {!state ? (
        <div className="loading">Loading colony...</div>
      ) : (
        <>
          <Controls
            playing={playing}
            onTogglePlay={() => setPlaying((p) => !p)}
            onStep={handleStep}
            onReset={handleReset}
            speed={speed}
            onSpeedChange={setSpeed}
            tick={state.tick}
          />

          <button className="btn btn-ghost scenario-toggle" onClick={() => setShowScenario((s) => !s)}>
            {showScenario ? "Hide scenario settings" : "Scenario settings"}
          </button>
          {showScenario && (
            <ScenarioPanel schema={schema.fields} scenario={scenario} onChange={setScenario} onApply={handleReset} />
          )}

          <div className="main-layout">
            <ColonyGraph3D
              nodes={state.nodes}
              edges={state.edges}
              ants={state.ants}
              raining={state.raining}
              rivalColony={state.colonies.length > 1}
            />
            <aside className="side-panel">
              <StatsPanel
                history={history}
                colonyIds={state.colonies}
                showInfection={!!state.cfg.disease_enabled}
                showSeason={!!state.cfg.drought_enabled}
              />
              <Legend rivalColony={state.colonies.length > 1} />
            </aside>
          </div>
        </>
      )}
    </>
  );
}

export default function App() {
  const [schema, setSchema] = useState(null);
  const [tab, setTab] = useState("colony");
  const [error, setError] = useState(null);

  useEffect(() => {
    getScenarioSchema()
      .then(setSchema)
      .catch((e) => setError(e.message));
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>Leafcutter Ant Colony</h1>
          <p className="muted">
            An agent-based simulation of an <em>Atta</em>-style leafcutter colony - caste division
            of labor, fungus-garden agriculture, and pheromone-trail foraging - rendered as a live
            3D colored graph, with a dozen biologically-grounded variants you can turn on and
            compare.
          </p>
        </div>
        <nav className="tabs">
          {TABS.map((t) => (
            <button
              key={t.id}
              className={`tab-btn ${tab === t.id ? "tab-btn-active" : ""}`}
              onClick={() => setTab(t.id)}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </header>

      {error && <div className="error-banner">{error}. Is the backend running on port 8010?</div>}

      {!schema ? (
        <div className="loading">Loading scenario options...</div>
      ) : (
        <>
          {tab === "colony" && <ColonyView schema={schema} />}
          {tab === "compare" && <ABCompare schema={schema} />}
          {tab === "experiments" && <SweepView schema={schema} />}
        </>
      )}

      <footer className="footer mono">
        <span>Mesa (Python) simulation + FastAPI + react-three-fiber</span>
        <span>Grounded in Holldobler &amp; Wilson, "The Leafcutter Ants" (2010) - see README</span>
      </footer>
    </div>
  );
}
