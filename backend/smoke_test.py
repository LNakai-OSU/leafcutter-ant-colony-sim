import sys
import time

from simulation import ColonyModel
from simulation import config as sim_config


def run(name, scenario=None, seed=42, n=2000, print_every=400):
    print(f"\n=== {name} ===")
    model = ColonyModel(seed=seed, scenario=scenario)
    print("colonies:", [c["id"] for c in model.colonies], "nodes:", model.graph.number_of_nodes(),
          "edges:", model.graph.number_of_edges())

    t0 = time.time()
    for i in range(n):
        model.step()
        if i % print_every == 0:
            h = model.history[-1]
            for cid, s in h["colonies"].items():
                print(f"tick {h['tick']:>4} [{cid}] pop={s['total_population']:>3} "
                      f"by_caste={s['population']} fungus={s['avg_fungus_health']:.1f} "
                      f"infection={s['avg_infection']:.2f} leaves={s['leaves_delivered']:.1f}")
    dt = time.time() - t0
    print(f"{n} ticks in {dt:.2f}s ({n/dt:.0f} ticks/sec)")
    return model


def main():
    baseline = run("baseline", scenario=None)
    assert baseline.schedule.get_agent_count() >= sum(sim_config.STARTING_COLONY.values())

    disease = run("disease", scenario={"disease_enabled": True}, n=3000)
    healthy_avg = baseline.history[-1]["colonies"]["A"]["avg_fungus_health"]
    diseased_avg = disease.history[-1]["colonies"]["A"]["avg_fungus_health"]
    print(f"healthy avg fungus={healthy_avg:.1f} vs diseased avg fungus={diseased_avg:.1f}")

    phorid = run("phorid_flies", scenario={"phorid_flies_enabled": True}, n=1500)

    drought = run("drought", scenario={"drought_enabled": True}, n=2500, print_every=500)
    rain_ticks = sum(1 for h in drought.history if h["raining"])
    print("ticks raining:", rain_ticks, "/", len(drought.history))

    defense = run("chemical_defense", scenario={"chemical_defense": True}, n=1500)

    finite = run("finite_trees", scenario={"finite_trees": True}, n=3000, print_every=500)
    dead_trees = sum(1 for n, d in finite.graph.nodes(data=True) if d["kind"] == "tree" and d.get("dead"))
    print("dead trees:", dead_trees, "/", sim_config.DEFAULT_SCENARIO["num_leaf_trees"])

    patchy = run("patchy_trees", scenario={"tree_layout": "patchy"}, n=500)

    pleo = run("pleometrosis", scenario={"founding_queens": 3}, n=500)
    print("pleometrosis start pop:", pleo.history[0]["colonies"]["A"]["total_population"])

    caste_override = run(
        "caste_override_all_media",
        scenario={"caste_override": {"minim": 0.1, "minor": 0.1, "media": 0.7, "major": 0.1}},
        n=1500,
    )

    rival = run("rival_colony", scenario={"rival_colony": True}, n=2000, print_every=500)
    assert set(rival.history[-1]["colonies"].keys()) == {"A", "B"}
    a_leaves = rival.history[-1]["colonies"]["A"]["leaves_delivered"]
    b_leaves = rival.history[-1]["colonies"]["B"]["leaves_delivered"]
    print(f"rival colony leaves: A={a_leaves:.1f} B={b_leaves:.1f}")

    everything = run(
        "kitchen_sink",
        scenario={
            "disease_enabled": True,
            "phorid_flies_enabled": True,
            "drought_enabled": True,
            "chemical_defense": True,
            "finite_trees": True,
            "tree_layout": "patchy",
            "rival_colony": True,
            "founding_queens": 2,
        },
        n=2000,
        print_every=500,
    )

    print("\nOK - all scenarios ran without error")


if __name__ == "__main__":
    sys.exit(main())
