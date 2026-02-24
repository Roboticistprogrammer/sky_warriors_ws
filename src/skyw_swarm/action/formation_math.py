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


def line_formation(spacing, drone_count, center, altitude, rotation):
    """
    Create a straight horizontal line centered at leader
    """

    desired = []

    offset = (drone_count - 1) / 2.0

    for i in range(drone_count):
        x = (i - offset) * spacing
        y = 0
        desired.append([x, y])

    desired = np.array(desired)

    desired = rotate_2d(desired, rotation)

    final = []
    for i in range(drone_count):
        final.append([
            center[0] + desired[i][0],
            center[1] + desired[i][1],
            altitude
        ])

    return np.array(final)


def v_formation(spacing, drone_count, center, altitude, rotation):
    """
    Leader at front.
    Others distributed equally on both wings.
    """

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

    final = []
    for i in range(drone_count):
        final.append([
            center[0] + desired[i][0],
            center[1] + desired[i][1],
            altitude
        ])

    return np.array(final)
