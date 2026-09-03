import { useCallback, useEffect, useRef, useState } from "react";
import ColonyGraph3D from "./components/ColonyGraph3D";
import Controls from "./components/Controls";
import StatsPanel from "./components/StatsPanel";
import Legend from "./components/Legend";
import { getState, stepSimulation, resetSimulation } from "./api";
import "./App.css";

const POLL_MS = 350;

export default function App() {
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
    resetSimulation().then(applyState).catch((e) => setError(e.message));
  };

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>Leafcutter Ant Colony</h1>
          <p className="muted">
            An agent-based simulation of an <em>Atta</em>-style leafcutter colony - caste
            division of labor, fungus-garden agriculture, and pheromone-trail foraging - rendered
            as a live 3D colored graph.
          </p>
        </div>
      </header>

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

          <div className="main-layout">
            <ColonyGraph3D nodes={state.nodes} edges={state.edges} ants={state.ants} />
            <aside className="side-panel">
              <StatsPanel history={history} />
              <Legend />
            </aside>
          </div>
        </>
      )}

      <footer className="footer mono">
        <span>Mesa (Python) simulation + FastAPI + react-three-fiber</span>
        <span>Grounded in Holldobler &amp; Wilson, "The Leafcutter Ants" (2010) - see README</span>
      </footer>
    </div>
  );
}
