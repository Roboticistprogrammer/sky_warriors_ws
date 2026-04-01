#!/usr/bin/env python3

import numpy as np
import math

def rotate_2d(points, angle_deg):
    angle = math.radians(angle_deg)
    R = np.array([
        [math.cos(angle), -math.sin(angle)],
        [math.sin(angle),  math.cos(angle)]
    ])
    return (R @ points.T).T


def _to_world(points_2d, center, altitude):
    """Lift 2D points into world coordinates at a fixed altitude."""
    final = []
    for i in range(points_2d.shape[0]):
        final.append([
            center[0] + points_2d[i][0],
            center[1] + points_2d[i][1],
            altitude
        ])
    return np.array(final)


def line_formation(spacing, drone_count, center, altitude, rotation):
    """Create a straight horizontal line centered at leader."""

    desired = []

    offset = (drone_count - 1) / 2.0

    for i in range(drone_count):
        x = (i - offset) * spacing
        y = 0
        desired.append([x, y])

    desired = np.array(desired)

    desired = rotate_2d(desired, rotation)

    return _to_world(desired, center, altitude)


def v_formation(spacing, drone_count, center, altitude, rotation):
    """Leader at front, others distributed equally on both wings."""

    desired = []
    desired.append([0, 0])  # leader

    wing_index = 1
    side = -1

    for i in range(1, drone_count):
        x = wing_index * spacing
        y = side * wing_index * spacing
        desired.append([x, y])

        side *= -1
        if side == -1:
            wing_index += 1

    desired = np.array(desired)
    desired = rotate_2d(desired, rotation)

    return _to_world(desired, center, altitude)


def arrow_head_formation(spacing, drone_count, center, altitude, rotation):
    """Arrow head with a V and a center tail behind the leader."""
    desired = []
    desired.append([0, 0])  # leader at tip

    row = 1
    while len(desired) < drone_count:
        # Left wing
        if len(desired) < drone_count:
            desired.append([-row * spacing, row * spacing])
        # Right wing
        if len(desired) < drone_count:
            desired.append([-row * spacing, -row * spacing])
        # Center tail
        if len(desired) < drone_count:
            desired.append([-row * spacing, 0])
        row += 1

    desired = np.array(desired)
    desired = rotate_2d(desired, rotation)
    return _to_world(desired, center, altitude)


FORMATION_BUILDERS = {
    "line": line_formation,
    "v": v_formation,
    "arrow_head": arrow_head_formation,
}
