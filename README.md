# Mission-Preservation Framework for Catastrophically Damaged UAVs

This repository contains a research baseline for deciding how a multirotor UAV
should use its remaining controllability after catastrophic actuator or rotor
damage. The objective is not to guarantee continued flight. It is to maximize
expected terminal mission utility while constraining risk to people, property,
and the vehicle.

## Scope

The current baseline is a deterministic, reduced-order 6-DOF simulation:

- rotor-health and actuator-loss scenarios;
- thrust-limited terminal descent;
- attitude and horizontal-velocity control under degraded authority;
- candidate landing-site feasibility and risk/utility scoring;
- mission value from camera pointing, communication, data transmission, and
  vehicle recoverability;
- reproducible JSON experiment output.

It is a research simulator, not flight-certified software. The model deliberately
separates **decision making** (which terminal objective to pursue) from
**control execution** (tracking a feasible descent command). Hardware-in-the-loop
validation, perception uncertainty, human-density estimation, and formal safety
assurance are future work.

## Quick start

The implementation uses only the Python standard library.

```powershell
C:/Users/varsh/AppData/Local/Python/pythoncore-3.14-64/python.exe -m unittest discover -s tests -v
C:/Users/varsh/AppData/Local/Python/pythoncore-3.14-64/python.exe -m terminal_uav.simulate --scenario one_rotor_loss --output results/one_rotor_loss.json
```

From the repository root, set `PYTHONPATH=src` if the package is not installed:

```powershell
$env:PYTHONPATH = "src"
```

## Research document

The LaTeX review and proposed evaluation protocol are in
[`docs/literature_review.tex`](docs/literature_review.tex). References are
included in [`docs/references.bib`](docs/references.bib).

The expanded IEEE-style paper includes generated figures in
[`docs/figures/`](docs/figures/) and scenario JSON outputs in
[`results/`](results/). Regenerate all results and figures with:

```powershell
$env:PYTHONPATH = "src"
python scripts\generate_figures.py
```

## Safety and ethics

The framework is intended for simulation and research planning. It must not be
used to command an aircraft without independent verification, geofencing,
certification, and a safety case. A mission-preservation objective is always
subordinate to constraints that protect people and critical infrastructure.
