export const NODE_COLOR = {
  entrance: "#f2ede2",
  queen: "#e6c34d",
  nursery: "#f0a3c4",
  waste: "#8a6a45",
  junction: "#6b7280",
  trunk: "#c99a5b",
  tree: "#5fae52",
  // fungus is a health-driven ramp, see fungusColor()
};

export const NODE_RADIUS = {
  entrance: 0.55,
  queen: 0.7,
  nursery: 0.42,
  waste: 0.4,
  junction: 0.28,
  trunk: 0.32,
  fungus: 0.5,
};

export const CASTE_COLOR = {
  minim: "#f2ede2",
  minor: "#8fb6c9",
  media: "#e0a83c",
  major: "#c9503f",
};

export const CASTE_LABEL = {
  minim: "Minim (fungus/brood care)",
  minor: "Minor (waste, backup fungus care)",
  media: "Media (primary forager)",
  major: "Major (guard)",
};

const FUNGUS_LOW = [122, 84, 43]; // dried-out brown
const FUNGUS_HIGH = [143, 214, 95]; // lush green

export function fungusColor(health) {
  const t = Math.max(0, Math.min(1, health / 100));
  const rgb = FUNGUS_LOW.map((lo, i) => Math.round(lo + (FUNGUS_HIGH[i] - lo) * t));
  return `rgb(${rgb.join(",")})`;
}

export function treeColor(biomass) {
  const t = Math.max(0.15, Math.min(1, biomass / 100));
  return `rgba(95, 174, 82, ${0.35 + t * 0.65})`;
}
