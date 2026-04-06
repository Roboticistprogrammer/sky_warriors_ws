#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    log_level = LaunchConfiguration('log_level')
    use_sim_time = LaunchConfiguration('use_sim_time')
    drone_count = LaunchConfiguration('drone_count')
    hover_z = LaunchConfiguration('hover_z')

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='clock_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
        output='screen',
    )

    offboard_helper = Node(
        package='skyw_control',
        executable='offboard_helper.py',
        name='offboard_helper',
        output='screen',
        arguments=['--ros-args', '--log-level', log_level],
        parameters=[{
            'drone_count': drone_count,
            'use_sim_time': use_sim_time,
            'hover_z': hover_z,
        }],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'log_level',
            default_value='info',
            description='Logging level for the mission stack.',
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation time for mission nodes.',
        ),
        DeclareLaunchArgument(
            'drone_count',
            default_value='3',
            description='Number of PX4 vehicles in the mission.',
        ),
        DeclareLaunchArgument(
            'hover_z',
            default_value='-5.0',
            description='Hover altitude in PX4 local NED frame.',
        ),
        clock_bridge,
        offboard_helper,
    ])

