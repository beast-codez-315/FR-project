"""Reduced-order terminal dynamics for a damaged multirotor.

The model is intentionally transparent rather than flight-ready. It is useful
for comparing decision policies and exposing assumptions before high-fidelity
or hardware-in-the-loop work.
"""

from dataclasses import dataclass, replace
import math
from typing import Tuple

Vector3 = Tuple[float, float, float]


def _add(a: Vector3, b: Vector3) -> Vector3:
    return tuple(x + y for x, y in zip(a, b))  # type: ignore[return-value]


def _scale(a: Vector3, value: float) -> Vector3:
    return tuple(value * x for x in a)  # type: ignore[return-value]


@dataclass(frozen=True)
class RotorHealth:
    """Remaining thrust fraction for four rotors, in front-left/front-right/rear-right/rear-left order."""

    fractions: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)

    def __post_init__(self) -> None:
        if len(self.fractions) != 4 or any(not 0.0 <= value <= 1.0 for value in self.fractions):
            raise ValueError("rotor health fractions must contain four values in [0, 1]")

    @property
    def total_fraction(self) -> float:
        return sum(self.fractions) / 4.0

    @property
    def asymmetry(self) -> float:
        return max(self.fractions) - min(self.fractions)


@dataclass(frozen=True)
class Scenario:
    name: str
    rotor_health: RotorHealth
    wind: Vector3 = (0.0, 0.0, 0.0)
    initial_altitude: float = 30.0
    initial_horizontal_speed: float = 3.0


@dataclass(frozen=True)
class VehicleState:
    position: Vector3
    velocity: Vector3
    attitude: Vector3
    angular_rate: Vector3
    time: float = 0.0

    @property
    def altitude(self) -> float:
        return self.position[2]

    @property
    def speed(self) -> float:
        return math.sqrt(sum(component * component for component in self.velocity))


def initial_state(scenario: Scenario) -> VehicleState:
    return VehicleState(
        position=(0.0, 0.0, scenario.initial_altitude),
        velocity=(scenario.initial_horizontal_speed, 0.0, 0.0),
        attitude=(0.0, 0.0, 0.0),
        angular_rate=(0.0, 0.0, 0.0),
    )


def step(
    state: VehicleState,
    scenario: Scenario,
    target_velocity: Vector3,
    dt: float = 0.1,
) -> VehicleState:
    """Advance the terminal model by one step with bounded degraded authority."""
    if dt <= 0.0:
        raise ValueError("dt must be positive")
    health = scenario.rotor_health
    authority = max(0.05, health.total_fraction * (1.0 - 0.35 * health.asymmetry))
    max_acceleration = 4.0 * authority
    desired_acceleration = _scale(
        tuple(target - actual for target, actual in zip(target_velocity, state.velocity)), 1.0 / dt
    )  # type: ignore[arg-type]
    acceleration_norm = math.sqrt(sum(component * component for component in desired_acceleration))
    if acceleration_norm > max_acceleration:
        desired_acceleration = _scale(desired_acceleration, max_acceleration / acceleration_norm)
    acceleration = _add(desired_acceleration, scenario.wind)
    velocity = _add(state.velocity, _scale(acceleration, dt))
    position = _add(state.position, _scale(velocity, dt))
    position = (position[0], position[1], max(0.0, position[2]))
    attitude = (
        max(-math.pi / 2, min(math.pi / 2, -velocity[1] * 0.04)),
        max(-math.pi / 2, min(math.pi / 2, velocity[0] * 0.04)),
        state.attitude[2],
    )
    angular_rate = _scale(
        tuple(new - old for new, old in zip(attitude, state.attitude)), 1.0 / dt
    )  # type: ignore[arg-type]
    return replace(
        state,
        position=position,
        velocity=velocity,
        attitude=attitude,
        angular_rate=angular_rate,
        time=state.time + dt,
    )
