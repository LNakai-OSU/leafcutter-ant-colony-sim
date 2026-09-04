import { useMemo } from "react";

const CASTES = ["minim", "minor", "media", "major"];

function groupFields(fields) {
  const groups = new Map();
  for (const f of fields) {
    if (!groups.has(f.group)) groups.set(f.group, []);
    groups.get(f.group).push(f);
  }
  return [...groups.entries()];
}

function Field({ field, value, onChange }) {
  if (field.type === "bool") {
    return (
      <label className="field field-bool" title={field.help}>
        <input type="checkbox" checked={!!value} onChange={(e) => onChange(e.target.checked)} />
        <span>{field.label}</span>
      </label>
    );
  }

  if (field.type === "select") {
    return (
      <label className="field" title={field.help}>
        <span>{field.label}</span>
        <select value={value} onChange={(e) => onChange(e.target.value)}>
          {field.options.map((o) => (
            <option key={o} value={o}>
              {o}
            </option>
          ))}
        </select>
      </label>
    );
  }

  if (field.type === "number") {
    return (
      <label className="field" title={field.help}>
        <span>
          {field.label} <span className="field-value mono">{value}</span>
        </span>
        <input
          type="range"
          min={field.min}
          max={field.max}
          step={field.step}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
        />
      </label>
    );
  }

  if (field.type === "caste_ratio") {
    const enabled = value != null;
    const ratios = value || { minim: 0.3, minor: 0.25, media: 0.35, major: 0.1 };
    return (
      <div className="field field-caste" title={field.help}>
        <label className="field-bool">
          <input
            type="checkbox"
            checked={enabled}
            onChange={(e) => onChange(e.target.checked ? ratios : null)}
          />
          <span>{field.label}</span>
        </label>
        {enabled && (
          <div className="caste-sliders">
            {CASTES.map((c) => (
              <label key={c} className="caste-slider">
                <span className="mono">{c}</span>
                <input
                  type="range"
                  min={0}
                  max={1}
                  step={0.05}
                  value={ratios[c]}
                  onChange={(e) => onChange({ ...ratios, [c]: Number(e.target.value) })}
                />
              </label>
            ))}
          </div>
        )}
      </div>
    );
  }

  return null;
}

export default function ScenarioPanel({ schema, scenario, onChange, onApply, applyLabel = "New colony" }) {
  const groups = useMemo(() => groupFields(schema), [schema]);

  return (
    <div className="scenario-panel">
      {groups.map(([group, fields]) => (
        <div className="scenario-group" key={group}>
          <h4>{group}</h4>
          {fields.map((f) => (
            <Field
              key={f.key}
              field={f}
              value={scenario[f.key]}
              onChange={(v) => onChange({ ...scenario, [f.key]: v })}
            />
          ))}
        </div>
      ))}
      <button className="btn btn-primary scenario-apply" onClick={onApply}>
        {applyLabel}
      </button>
    </div>
  );
}
