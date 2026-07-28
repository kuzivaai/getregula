# synthetic-test-fixture
"""Synthetic fixture: Annex III Category 2 — critical infrastructure.
Expected: high_risk."""


def water_supply_chlorination_control(turbidity, flow_rate):
    """Sets dosing for a municipal water supply plant without operator sign-off."""
    dose = model.infer([turbidity, flow_rate])
    actuator.set_dose(dose)
    return dose
