import { AreaChart, Area, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";
import { CASTE_COLOR, COLONY_TINT } from "../theme";

const tooltipStyle = { background: "var(--surface)", border: "1px solid var(--border)", fontSize: 12 };

export default function StatsPanel({ history, colonyIds, showInfection, showSeason }) {
  const data = history.map((h) => {
    const row = { tick: h.tick, season: h.season_multiplier, raining: h.raining ? 1 : 0 };
    for (const cid of colonyIds) {
      const s = h.colonies[cid];
      if (!s) continue;
      row[`${cid}_total`] = s.total_population;
      row[`${cid}_fungus`] = s.avg_fungus_health;
      row[`${cid}_infection`] = Math.round(s.avg_infection * 1000) / 10;
      row[`${cid}_leaves`] = s.leaves_delivered;
      if (colonyIds.length === 1) {
        row.minim = s.population.minim;
        row.minor = s.population.minor;
        row.media = s.population.media;
        row.major = s.population.major;
      }
    }
    return row;
  });

  const multi = colonyIds.length > 1;

  return (
    <div className="stats-panel">
      <div className="stats-block">
        <h3>Population{multi ? " by colony" : " by caste"}</h3>
        <ResponsiveContainer width="100%" height={160}>
          <AreaChart data={data}>
            <CartesianGrid stroke="var(--grid-line)" vertical={false} />
            <XAxis dataKey="tick" stroke="var(--muted)" fontSize={11} />
            <YAxis stroke="var(--muted)" fontSize={11} width={30} />
            <Tooltip contentStyle={tooltipStyle} />
            {multi ? (
              colonyIds.map((cid) => (
                <Area
                  key={cid}
                  type="monotone"
                  dataKey={`${cid}_total`}
                  name={`colony ${cid}`}
                  stroke={COLONY_TINT[cid]}
                  fill={COLONY_TINT[cid]}
                  fillOpacity={0.25}
                />
              ))
            ) : (
              <>
                <Area type="monotone" dataKey="minim" stackId="1" stroke={CASTE_COLOR.minim} fill={CASTE_COLOR.minim} fillOpacity={0.5} />
                <Area type="monotone" dataKey="minor" stackId="1" stroke={CASTE_COLOR.minor} fill={CASTE_COLOR.minor} fillOpacity={0.5} />
                <Area type="monotone" dataKey="media" stackId="1" stroke={CASTE_COLOR.media} fill={CASTE_COLOR.media} fillOpacity={0.5} />
                <Area type="monotone" dataKey="major" stackId="1" stroke={CASTE_COLOR.major} fill={CASTE_COLOR.major} fillOpacity={0.5} />
              </>
            )}
            {multi && <Legend wrapperStyle={{ fontSize: 11 }} />}
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="stats-block">
        <h3>Avg. fungus garden health</h3>
        <ResponsiveContainer width="100%" height={120}>
          <LineChart data={data}>
            <CartesianGrid stroke="var(--grid-line)" vertical={false} />
            <XAxis dataKey="tick" stroke="var(--muted)" fontSize={11} />
            <YAxis stroke="var(--muted)" fontSize={11} width={30} domain={[0, 100]} />
            <Tooltip contentStyle={tooltipStyle} />
            {colonyIds.map((cid) => (
              <Line
                key={cid}
                type="monotone"
                dataKey={`${cid}_fungus`}
                name={multi ? `colony ${cid}` : "fungus health"}
                stroke={multi ? COLONY_TINT[cid] : "#8fd65f"}
                dot={false}
                strokeWidth={2}
              />
            ))}
            {multi && <Legend wrapperStyle={{ fontSize: 11 }} />}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {showInfection && (
        <div className="stats-block">
          <h3>Escovopsis infection (% of fungus garden)</h3>
          <ResponsiveContainer width="100%" height={120}>
            <LineChart data={data}>
              <CartesianGrid stroke="var(--grid-line)" vertical={false} />
              <XAxis dataKey="tick" stroke="var(--muted)" fontSize={11} />
              <YAxis stroke="var(--muted)" fontSize={11} width={30} domain={[0, 100]} />
              <Tooltip contentStyle={tooltipStyle} />
              {colonyIds.map((cid) => (
                <Line
                  key={cid}
                  type="monotone"
                  dataKey={`${cid}_infection`}
                  name={multi ? `colony ${cid}` : "infection"}
                  stroke={multi ? COLONY_TINT[cid] : "#b23fa8"}
                  dot={false}
                  strokeWidth={2}
                />
              ))}
              {multi && <Legend wrapperStyle={{ fontSize: 11 }} />}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="stats-block">
        <h3>Cumulative leaf biomass delivered</h3>
        <ResponsiveContainer width="100%" height={120}>
          <LineChart data={data}>
            <CartesianGrid stroke="var(--grid-line)" vertical={false} />
            <XAxis dataKey="tick" stroke="var(--muted)" fontSize={11} />
            <YAxis stroke="var(--muted)" fontSize={11} width={30} />
            <Tooltip contentStyle={tooltipStyle} />
            {colonyIds.map((cid) => (
              <Line
                key={cid}
                type="monotone"
                dataKey={`${cid}_leaves`}
                name={multi ? `colony ${cid}` : "leaves"}
                stroke={multi ? COLONY_TINT[cid] : "#e0a83c"}
                dot={false}
                strokeWidth={2}
              />
            ))}
            {multi && <Legend wrapperStyle={{ fontSize: 11 }} />}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {showSeason && (
        <div className="stats-block">
          <h3>Season (regrowth multiplier)</h3>
          <ResponsiveContainer width="100%" height={90}>
            <LineChart data={data}>
              <CartesianGrid stroke="var(--grid-line)" vertical={false} />
              <XAxis dataKey="tick" stroke="var(--muted)" fontSize={11} />
              <YAxis stroke="var(--muted)" fontSize={11} width={30} />
              <Tooltip contentStyle={tooltipStyle} />
              <Line type="monotone" dataKey="season" stroke="#6fb8d9" dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
