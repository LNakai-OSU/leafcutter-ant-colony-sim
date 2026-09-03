const SPEEDS = [
  { label: "1x", ticksPerPoll: 1 },
  { label: "3x", ticksPerPoll: 3 },
  { label: "8x", ticksPerPoll: 8 },
  { label: "20x", ticksPerPoll: 20 },
];

export default function Controls({ playing, onTogglePlay, onStep, onReset, speed, onSpeedChange, tick }) {
  return (
    <div className="controls">
      <div className="controls-row">
        <button className="btn btn-primary" onClick={onTogglePlay}>
          {playing ? "Pause" : "Play"}
        </button>
        <button className="btn btn-ghost" onClick={onStep} disabled={playing}>
          Step +1
        </button>
        <button className="btn btn-ghost" onClick={onReset}>
          New colony
        </button>
      </div>
      <div className="controls-row">
        <span className="controls-label mono">speed</span>
        {SPEEDS.map((s) => (
          <button
            key={s.label}
            className={`chip-btn ${speed === s.ticksPerPoll ? "chip-btn-active" : ""}`}
            onClick={() => onSpeedChange(s.ticksPerPoll)}
          >
            {s.label}
          </button>
        ))}
        <span className="controls-tick mono">tick {tick}</span>
      </div>
    </div>
  );
}
