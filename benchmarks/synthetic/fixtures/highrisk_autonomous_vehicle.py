# synthetic-test-fixture
"""Synthetic fixture: safety components — autonomous driving.
Expected: high_risk."""


def autonomous_vehicle_planner(lidar_frame, camera_frame):
    """Plans steering and braking for a self-driving shuttle."""
    return _policy.act(_fuse(lidar_frame, camera_frame))
