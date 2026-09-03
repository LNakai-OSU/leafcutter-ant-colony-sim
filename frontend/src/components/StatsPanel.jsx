import { AreaChart, Area, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { CASTE_COLOR } from "../theme";

export default function StatsPanel({ history }) {
  const data = history.map((h) => ({
    tick: h.tick,
    minim: h.population.minim,
    minor: h.population.minor,
    media: h.population.media,
    major: h.population.major,
    total: h.total_population,
    fungus: h.avg_fungus_health,
    leaves: h.leaves_delivered,
  }));

  return (
    <div className="stats-panel">
      <div className="stats-block">
        <h3>Population by caste</h3>
        <ResponsiveContainer width="100%" height={160}>
          <AreaChart data={data}>
            <CartesianGrid stroke="var(--grid-line)" vertical={false} />
            <XAxis dataKey="tick" stroke="var(--muted)" fontSize={11} />
            <YAxis stroke="var(--muted)" fontSize={11} width={30} />
            <Tooltip
              contentStyle={{ background: "var(--surface)", border: "1px solid var(--border)", fontSize: 12 }}
            />
            <Area type="monotone" dataKey="minim" stackId="1" stroke={CASTE_COLOR.minim} fill={CASTE_COLOR.minim} fillOpacity={0.5} />
            <Area type="monotone" dataKey="minor" stackId="1" stroke={CASTE_COLOR.minor} fill={CASTE_COLOR.minor} fillOpacity={0.5} />
            <Area type="monotone" dataKey="media" stackId="1" stroke={CASTE_COLOR.media} fill={CASTE_COLOR.media} fillOpacity={0.5} />
            <Area type="monotone" dataKey="major" stackId="1" stroke={CASTE_COLOR.major} fill={CASTE_COLOR.major} fillOpacity={0.5} />
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
            <Tooltip
              contentStyle={{ background: "var(--surface)", border: "1px solid var(--border)", fontSize: 12 }}
            />
            <Line type="monotone" dataKey="fungus" stroke="#8fd65f" dot={false} strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="stats-block">
        <h3>Cumulative leaf biomass delivered</h3>
        <ResponsiveContainer width="100%" height={120}>
          <LineChart data={data}>
            <CartesianGrid stroke="var(--grid-line)" vertical={false} />
            <XAxis dataKey="tick" stroke="var(--muted)" fontSize={11} />
            <YAxis stroke="var(--muted)" fontSize={11} width={30} />
            <Tooltip
              contentStyle={{ background: "var(--surface)", border: "1px solid var(--border)", fontSize: 12 }}
            />
            <Line type="monotone" dataKey="leaves" stroke="#e0a83c" dot={false} strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
