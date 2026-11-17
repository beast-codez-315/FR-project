import unittest

from terminal_uav.decision import CandidateSite, choose_landing_site, choose_terminal_objective
from terminal_uav.model import RotorHealth, Scenario, initial_state, step


class FrameworkTests(unittest.TestCase):
    def test_invalid_rotor_health_is_rejected(self):
        with self.assertRaises(ValueError):
            RotorHealth((1.0, 1.0, 1.0, 1.2))

    def test_step_reduces_descent_altitude(self):
        scenario = Scenario("test", RotorHealth((0.0, 1.0, 1.0, 1.0)))
        state = initial_state(scenario)
        next_state = step(state, scenario, (0.0, 0.0, -1.0))
        self.assertLess(next_state.altitude, state.altitude)

    def test_human_exposure_is_hard_constraint(self):
        dangerous = CandidateSite("road", 2.0, 1.0, 1.0, 0.9, 1.0, 1.0, 1.0)
        safe = CandidateSite("field", 5.0, 0.9, 0.9, 0.05, 0.4, 0.2, 0.4)
        selected = choose_landing_site([dangerous, safe])
        self.assertIsNotNone(selected)
        self.assertEqual(selected.site.name, "field")

    def test_objective_prioritizes_safety(self):
        self.assertEqual(choose_terminal_objective(10.0, 1.0, 1.0, False), "minimize_human_exposure")
        self.assertEqual(choose_terminal_objective(10.0, 1.0, 1.0, True), "transmit_and_observe")


if __name__ == "__main__":
    unittest.main()
