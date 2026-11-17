"""Generate paper figures from the reproducible terminal-UAV simulator."""

import json
from pathlib import Path

import matplotlib.pyplot as plt

from terminal_uav.simulate import SCENARIOS, run


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "docs" / "figures"
RESULTS = ROOT / "results"


def save_results() -> dict[str, dict]:
    RESULTS.mkdir(exist_ok=True)
    all_results = {}
    for name, scenario in SCENARIOS.items():
        result = run(scenario)
        all_results[name] = result
        (RESULTS / f"{name}.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return all_results


def plot_trajectory(results: dict[str, dict]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.8), constrained_layout=True)
    for name, result in results.items():
        samples = result["samples"]
        axes[0].plot([p[0] for p in (s["position"] for s in samples)],
                     [p[1] for p in (s["position"] for s in samples)], label=name.replace("_", " "))
        axes[1].plot([s["time"] for s in samples],
                     [s["position"][2] for s in samples], label=name.replace("_", " "))
    axes[0].set(xlabel="x position (m)", ylabel="y position (m)", title="Horizontal trajectory")
    axes[1].set(xlabel="Time (s)", ylabel="Altitude (m)", title="Terminal descent")
    axes[0].grid(alpha=0.25)
    axes[1].grid(alpha=0.25)
    axes[1].legend(fontsize=7)
    fig.savefig(FIGURES / "trajectory_and_altitude.png", dpi=300)
    plt.close(fig)


def plot_velocity(results: dict[str, dict]) -> None:
    fig, ax = plt.subplots(figsize=(5.8, 3.0), constrained_layout=True)
    for name, result in results.items():
        samples = result["samples"]
        speed = [(sum(v * v for v in s["velocity"]) ** 0.5) for s in samples]
        ax.plot([s["time"] for s in samples], speed, label=name.replace("_", " "))
    ax.set(xlabel="Time (s)", ylabel="Speed magnitude (m/s)", title="Degraded terminal speed")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=7)
    fig.savefig(FIGURES / "speed_comparison.png", dpi=300)
    plt.close(fig)


def plot_summary(results: dict[str, dict]) -> None:
    names = list(results)
    landing_speed = [results[name]["landing_speed"] for name in names]
    landing_time = [results[name]["landing_time"] for name in names]
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.7), constrained_layout=True)
    labels = [name.replace("_", "\n") for name in names]
    axes[0].bar(labels, landing_speed, color="#4472C4")
    axes[0].set_ylabel("Terminal speed (m/s)")
    axes[0].set_title("Terminal-speed proxy")
    axes[1].bar(labels, landing_time, color="#70AD47")
    axes[1].set_ylabel("End time (s)")
    axes[1].set_title("End of simulation horizon")
    for axis in axes:
        axis.grid(axis="y", alpha=0.25)
    fig.savefig(FIGURES / "scenario_summary.png", dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    FIGURES.mkdir(parents=True, exist_ok=True)
    results = save_results()
    plot_trajectory(results)
    plot_velocity(results)
    plot_summary(results)
    print(f"Generated figures in {FIGURES}")
