"""Command-line experiment runner for the mission-preservation baseline."""

import argparse
import json
from pathlib import Path

from .decision import CandidateSite, choose_landing_site, choose_terminal_objective
from .model import RotorHealth, Scenario, initial_state, step


SCENARIOS = {
    "one_rotor_loss": Scenario("one_rotor_loss", RotorHealth((0.0, 1.0, 1.0, 1.0))),
    "two_rotor_loss": Scenario("two_rotor_loss", RotorHealth((0.0, 1.0, 0.0, 1.0))),
    "windy_partial_failure": Scenario(
        "windy_partial_failure", RotorHealth((0.2, 0.8, 1.0, 0.7)), wind=(0.2, -0.1, 0.0)
    ),
}


def run(scenario: Scenario, duration: float = 30.0, dt: float = 0.1) -> dict:
    state = initial_state(scenario)
    target = (0.0, 0.0, -1.5)
    samples = []
    while state.time < duration and state.altitude > 0.0:
        state = step(state, scenario, target, dt)
        if len(samples) == 0 or int(state.time * 2) > int(samples[-1]["time"] * 2):
            samples.append(
                {"time": round(state.time, 2), "position": [round(x, 3) for x in state.position],
                 "velocity": [round(x, 3) for x in state.velocity]}
            )
    return {
        "scenario": scenario.name,
        "contact": state.altitude <= 0.0,
        "landing_time": round(state.time, 3),
        "landing_position": [round(x, 3) for x in state.position],
        "landing_speed": round(state.speed, 3),
        "samples": samples,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=sorted(SCENARIOS), default="one_rotor_loss")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    sites = [
        CandidateSite("open_field", 14.0, 0.95, 0.9, 0.05, 0.8, 0.2, 0.5),
        CandidateSite("communications_corridor", 8.0, 0.7, 0.65, 0.1, 0.5, 0.9, 0.95),
        CandidateSite("urban_roof", 5.0, 0.8, 0.8, 0.8, 0.9, 0.7, 0.9),
    ]
    selected = choose_landing_site(sites)
    result = run(SCENARIOS[args.scenario])
    result["selected_site"] = selected.site.name if selected else None
    result["terminal_objective"] = choose_terminal_objective(20.0, 0.8, 0.8, selected is not None)
    payload = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
