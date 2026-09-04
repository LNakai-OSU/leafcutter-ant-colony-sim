from .model import ColonyModel


def run_sweep(param_x, x_values, param_y, y_values, ticks, seed, base_scenario=None):
    """Runs one headless ColonyModel per (x, y) combination and returns each
    run's final stats. No rendering involved - this is purely for the
    Experiments/parameter-sweep view, reusing the exact same model used
    for the interactive simulation."""
    base = dict(base_scenario or {})
    grid = []
    for x in x_values:
        row = []
        for y in y_values:
            scenario = dict(base)
            scenario[param_x] = x
            scenario[param_y] = y
            model = ColonyModel(seed=seed, scenario=scenario)
            for _ in range(ticks):
                model.step()
            colony_stats = model.history[-1]["colonies"]["A"]
            row.append(
                {
                    "x": x,
                    "y": y,
                    "total_population": colony_stats["total_population"],
                    "avg_fungus_health": colony_stats["avg_fungus_health"],
                    "avg_infection": colony_stats["avg_infection"],
                    "leaves_delivered": colony_stats["leaves_delivered"],
                }
            )
        grid.append(row)
    return grid
