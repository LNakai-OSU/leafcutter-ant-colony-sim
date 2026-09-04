import { CASTE_COLOR, CASTE_LABEL, NODE_COLOR } from "../theme";

const CHAMBER_LEGEND = [
  { kind: "queen", label: "Queen chamber" },
  { kind: "nursery", label: "Nursery (brood)" },
  { kind: "fungus", label: "Fungus garden (green = healthy, magenta = infected)", swatch: "linear-gradient(90deg, #7a542b, #8fd65f, #b23fa8)" },
  { kind: "waste", label: "Waste chamber" },
  { kind: "junction", label: "Tunnel junction" },
  { kind: "trunk", label: "Trail junction (surface)" },
  { kind: "tree", label: "Leaf source tree (dim = dead)" },
  { kind: "entrance", label: "Nest entrance" },
];

export default function Legend({ rivalColony }) {
  return (
    <div className="legend">
      <div className="legend-group">
        <h4>Chambers &amp; trail nodes</h4>
        {CHAMBER_LEGEND.map((c) => (
          <div className="legend-row" key={c.kind}>
            <span
              className="legend-swatch"
              style={{ background: c.swatch || NODE_COLOR[c.kind] }}
            />
            <span>{c.label}</span>
          </div>
        ))}
      </div>
      <div className="legend-group">
        <h4>Ants by caste</h4>
        {Object.entries(CASTE_LABEL).map(([caste, label]) => (
          <div className="legend-row" key={caste}>
            <span className="legend-swatch legend-dot" style={{ background: CASTE_COLOR[caste] }} />
            <span>{label}</span>
          </div>
        ))}
      </div>
      {rivalColony && (
        <div className="legend-group">
          <h4>Colonies</h4>
          <p className="legend-note">
            Each colony's nest chambers carry a thin colored ring (amber = colony A, blue =
            colony B). Trees near the midpoint connect to both colonies' trails and are a
            shared, contested resource.
          </p>
        </div>
      )}
      <div className="legend-group">
        <h4>Trails</h4>
        <p className="legend-note">
          Surface-trail edge brightness &amp; thickness = pheromone concentration - trails
          strengthen as successful foragers reinforce the route back to a tree, and fade
          when unused.
        </p>
      </div>
    </div>
  );
}
