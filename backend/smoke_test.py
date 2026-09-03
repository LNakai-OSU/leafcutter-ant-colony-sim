import sys
import time

from simulation import ColonyModel


def main():
    model = ColonyModel(seed=42)
    print("graph nodes:", model.graph.number_of_nodes(), "edges:", model.graph.number_of_edges())
    print("initial population:", model.schedule.get_agent_count())

    t0 = time.time()
    n = 3000
    for i in range(n):
        model.step()
        if i % 300 == 0:
            h = model.history[-1]
            print(f"tick {h['tick']:>4}  pop={h['total_population']:>3}  "
                  f"by_caste={h['population']}  fungus={h['avg_fungus_health']:.1f}  "
                  f"leaves={h['leaves_delivered']:.1f}")
    dt = time.time() - t0
    print(f"\n{n} ticks in {dt:.2f}s ({n/dt:.0f} ticks/sec)")

    # sanity checks
    pher_values = [d["pheromone"] for u, v, d in model.graph.edges(data=True)
                   if model.graph.nodes[u]["domain"] == "surface" or model.graph.nodes[v]["domain"] == "surface"]
    print("surface pheromone range:", min(pher_values), max(pher_values))
    tree_biomass = [d["biomass"] for _, d in model.graph.nodes(data=True) if d["kind"] == "tree"]
    print("tree biomass range:", min(tree_biomass), max(tree_biomass))

    assert model.schedule.get_agent_count() >= sum(__import__("simulation.config", fromlist=["STARTING_COLONY"]).STARTING_COLONY.values()), \
        "population should not shrink below starting size (no deaths modeled yet)"
    assert max(pher_values) > 0.02, "expected at least one reinforced trail after 300 ticks"
    print("\nOK")


if __name__ == "__main__":
    sys.exit(main())
