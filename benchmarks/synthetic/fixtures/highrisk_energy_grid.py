# synthetic-test-fixture
"""Synthetic fixture: Annex III Category 2 — critical infrastructure.
Expected: high_risk."""


class LoadBalancer:
    """Predictive controller for regional energy grid dispatch."""

    def energy_grid_forecast(self, sensor_window):
        return self.model.predict(sensor_window)

    def shed_load(self, forecast):
        """Automatically sheds substations when demand exceeds capacity."""
        return [s for s in self.substations if forecast[s] > self.caps[s]]
