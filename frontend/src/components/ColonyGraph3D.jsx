import { useMemo, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Line, Instances, Instance, Html } from "@react-three/drei";
import * as THREE from "three";
import { NODE_COLOR, NODE_RADIUS, CASTE_COLOR, COLONY_TINT, fungusColor, treeColor } from "../theme";

function nodeColor(node) {
  if (node.kind === "fungus") return fungusColor(node.health ?? 60, node.infection ?? 0);
  if (node.kind === "tree") return treeColor(node.biomass ?? 60, node.dead);
  return NODE_COLOR[node.kind] || "#999999";
}

function nodeRadius(node) {
  if (node.kind === "tree") {
    const t = Math.max(0.2, Math.min(1, (node.biomass ?? 60) / 100));
    return 0.3 + t * 0.5;
  }
  return NODE_RADIUS[node.kind] ?? 0.3;
}

function Nodes({ nodes, hovered, setHovered, rivalColony }) {
  return (
    <group>
      {nodes.map((n) => (
        <group key={n.id} position={n.pos}>
          <mesh
            onPointerOver={(e) => {
              e.stopPropagation();
              setHovered(n);
            }}
            onPointerOut={() => setHovered((h) => (h && h.id === n.id ? null : h))}
          >
            <sphereGeometry args={[nodeRadius(n), 20, 20]} />
            <meshStandardMaterial
              color={nodeColor(n)}
              emissive={nodeColor(n)}
              emissiveIntensity={n.kind === "fungus" || n.kind === "queen" ? 0.5 : 0.15}
              roughness={0.55}
            />
          </mesh>
          {rivalColony && n.colony && n.kind !== "tree" && (
            <mesh>
              <ringGeometry args={[nodeRadius(n) * 1.35, nodeRadius(n) * 1.5, 24]} />
              <meshBasicMaterial color={COLONY_TINT[n.colony]} transparent opacity={0.6} side={THREE.DoubleSide} />
            </mesh>
          )}
          {hovered && hovered.id === n.id && (
            <Html distanceFactor={12} style={{ pointerEvents: "none" }}>
              <div className="node-tooltip">
                <strong>{n.id}</strong>
                <span>{n.kind}</span>
                {n.colony && <span>colony {n.colony}</span>}
                {n.health != null && <span>fungus health: {n.health}</span>}
                {n.infection > 0 && <span>infection: {(n.infection * 100).toFixed(0)}%</span>}
                {n.biomass != null && <span>leaf biomass: {n.biomass}{n.dead ? " (dead)" : ""}</span>}
                {n.acceptance != null && n.acceptance < 1 && <span>acceptance: {(n.acceptance * 100).toFixed(0)}%</span>}
                {n.brood != null && <span>brood: {n.brood}</span>}
              </div>
            </Html>
          )}
        </group>
      ))}
    </group>
  );
}

function Edges({ edges, nodeById }) {
  return (
    <group>
      {edges.map((e) => {
        const a = nodeById.get(e.source);
        const b = nodeById.get(e.target);
        if (!a || !b) return null;
        const isSurface = e.surface;
        const strength = isSurface ? Math.min(1, e.pheromone) : 0.18;
        const color = isSurface
          ? new THREE.Color("#e0a83c").lerp(new THREE.Color("#3a2f1c"), 1 - strength)
          : new THREE.Color("#5b5648");
        return (
          <Line
            key={`${e.source}-${e.target}`}
            points={[a.pos, b.pos]}
            color={color}
            lineWidth={isSurface ? 1 + strength * 3.5 : 1}
            transparent
            opacity={isSurface ? 0.35 + strength * 0.65 : 0.35}
          />
        );
      })}
    </group>
  );
}

function Ants({ ants, nodeById }) {
  const positions = useMemo(() => {
    return ants.map((a) => {
      if (!a.edge) {
        const n = nodeById.get(a.node);
        return n ? n.pos : [0, 0, 0];
      }
      const from = nodeById.get(a.edge[0]);
      const to = nodeById.get(a.edge[1]);
      if (!from || !to) return [0, 0, 0];
      const t = a.t;
      return [
        from.pos[0] + (to.pos[0] - from.pos[0]) * t,
        from.pos[1] + (to.pos[1] - from.pos[1]) * t,
        from.pos[2] + (to.pos[2] - from.pos[2]) * t,
      ];
    });
  }, [ants, nodeById]);

  return (
    <Instances limit={900}>
      <sphereGeometry args={[0.13, 8, 8]} />
      <meshStandardMaterial />
      {ants.map((a, i) => (
        <Instance key={a.id} position={positions[i]} color={CASTE_COLOR[a.caste]} />
      ))}
    </Instances>
  );
}

export default function ColonyGraph3D({ nodes, edges, ants, raining, rivalColony }) {
  const [hovered, setHovered] = useState(null);
  const nodeById = useMemo(() => new Map(nodes.map((n) => [n.id, n])), [nodes]);
  const bg = raining ? "#0b1016" : "#0d0b08";

  return (
    <div className="graph-canvas">
      {raining && <div className="rain-badge">raining - foraging paused outdoors</div>}
      <Canvas camera={{ position: [15, 11, 17], fov: 48 }}>
        <color attach="background" args={[bg]} />
        <fog attach="fog" args={[bg, 30, 90]} />
        <ambientLight intensity={raining ? 0.4 : 0.55} />
        <directionalLight position={[15, 25, 10]} intensity={raining ? 0.7 : 1.1} />
        <directionalLight position={[-15, -10, -10]} intensity={0.25} />
        <Nodes nodes={nodes} hovered={hovered} setHovered={setHovered} rivalColony={rivalColony} />
        <Edges edges={edges} nodeById={nodeById} />
        <Ants ants={ants} nodeById={nodeById} />
        <gridHelper args={[80, 40, "#33291a", "#201a10"]} position={[0, 0, 0]} />
        <OrbitControls makeDefault minDistance={6} maxDistance={70} />
      </Canvas>
    </div>
  );
}
