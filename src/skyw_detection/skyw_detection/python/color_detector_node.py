#!/usr/bin/env python3

from __future__ import annotations

import os
import time
from typing import Dict, Optional

import numpy as np
import rclpy
import yaml
from ament_index_python.packages import get_package_share_directory
from cv_bridge import CvBridge
from geometry_msgs.msg import PoseArray, Pose, Quaternion
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, ReliabilityPolicy, QoSProfile
from sensor_msgs.msg import Image
from std_msgs.msg import Header
from visualization_msgs.msg import Marker, MarkerArray

from .color_detector import ColorDetector
from .utils import (
    estimate_depth_from_diameter_px,
    pixel_to_camera_xyz,
    rotation_matrix_from_rpy,
    rotate_vector_by_quaternion,
)


class ColorDetectorNode(Node):
    """ROS2 node: detect red/blue pads from HSV masks and publish poses + RViz markers."""

    def __init__(self) -> None:
        super().__init__("color_detector_node")

        def as_bool(v) -> bool:
            if isinstance(v, bool):
                return v
            if isinstance(v, str):
                return v.strip().lower() in ("true", "1", "yes", "y", "on")
            return bool(v)

        def as_list3(v) -> list[float]:
            if isinstance(v, (list, tuple)) and len(v) == 3:
                return [float(v[0]), float(v[1]), float(v[2])]
            if isinstance(v, str):
                parsed = yaml.safe_load(v)
                if isinstance(parsed, (list, tuple)) and len(parsed) == 3:
                    return [float(parsed[0]), float(parsed[1]), float(parsed[2])]
            raise ValueError(f"Expected a 3-item list for parameter, got: {v!r}")
        
if __name__ == "__main__":
    main()
