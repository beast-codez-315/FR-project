"""Mission-aware terminal objective and landing-site selection."""

from dataclasses import dataclass
import math
from typing import Iterable, Optional


@dataclass(frozen=True)
class CandidateSite:
    name: str
    distance: float
    flatness: float
    obstacle_clearance: float
    human_exposure: float
    recovery_access: float
    mission_value: float
    communication_quality: float


@dataclass(frozen=True)
class MissionWeights:
    landing_safety: float = 0.45
    mission_value: float = 0.20
    recoverability: float = 0.15
    communication: float = 0.10
    impact_energy: float = 0.10


@dataclass(frozen=True)
class SiteScore:
    site: CandidateSite
    score: float
    feasible: bool
    rationale: str


def score_site(
    site: CandidateSite,
    weights: MissionWeights = MissionWeights(),
    available_time: float = 20.0,
    horizontal_speed: float = 3.0,
) -> SiteScore:
    """Score a site while making hard safety constraints explicit."""
    if available_time <= 0.0:
        raise ValueError("available_time must be positive")
    reachable = site.distance <= max(0.0, horizontal_speed * available_time)
    feasible = (
        reachable
        and site.flatness >= 0.35
        and site.obstacle_clearance >= 0.4
        and site.human_exposure <= 0.35
    )
    reachability = max(0.0, 1.0 - site.distance / max(horizontal_speed * available_time, 1e-6))
    safety = 0.4 * site.flatness + 0.4 * site.obstacle_clearance + 0.2 * (1.0 - site.human_exposure)
    energy = max(0.0, 1.0 - site.distance / max(horizontal_speed * available_time, 1e-6))
    score = (
        weights.landing_safety * safety
        + weights.mission_value * site.mission_value
        + weights.recoverability * site.recovery_access
        + weights.communication * site.communication_quality
        + weights.impact_energy * (0.5 * energy + 0.5 * reachability)
    )
    if not feasible:
        score -= 2.0
    rationale = "feasible" if feasible else "rejected by reachability, geometry, or human-exposure constraint"
    return SiteScore(site, score, feasible, rationale)


def choose_landing_site(
    sites: Iterable[CandidateSite],
    weights: MissionWeights = MissionWeights(),
    available_time: float = 20.0,
    horizontal_speed: float = 3.0,
) -> Optional[SiteScore]:
    scored = [score_site(site, weights, available_time, horizontal_speed) for site in sites]
    feasible = [item for item in scored if item.feasible]
    return max(feasible, key=lambda item: item.score) if feasible else None


def choose_terminal_objective(
    remaining_flight_time: float,
    data_remaining: float,
    communication_quality: float,
    safe_site_available: bool,
) -> str:
    """Select a mission mode; safety dominates when no safe site is available."""
    if remaining_flight_time <= 0.0:
        raise ValueError("remaining_flight_time must be positive")
    if not 0.0 <= data_remaining <= 1.0 or not 0.0 <= communication_quality <= 1.0:
        raise ValueError("data_remaining and communication_quality must be in [0, 1]")
    if not safe_site_available:
        return "minimize_human_exposure"
    if data_remaining > 0.2 and communication_quality > 0.4 and remaining_flight_time >= 5.0:
        return "transmit_and_observe"
    return "recoverable_landing"
