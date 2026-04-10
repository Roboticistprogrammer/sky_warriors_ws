#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('drone_id', default_value='1'),
        DeclareLaunchArgument('drone_ns_prefix', default_value='/drone'),
        DeclareLaunchArgument('target_x', default_value='0.0'),
        DeclareLaunchArgument('target_y', default_value='0.0'),
        DeclareLaunchArgument('target_z', default_value='-2.5'),
        DeclareLaunchArgument('target_yaw', default_value='0.0'),
        DeclareLaunchArgument('rate_hz', default_value='20.0'),
        DeclareLaunchArgument('frame_id', default_value='map'),
        DeclareLaunchArgument('log_level', default_value='info'),
        Node(
            package='skyw_swarm',
            executable='single_drone_setpoint.py',
            name='single_drone_setpoint',
            output='screen',
            arguments=['--ros-args', '--log-level', LaunchConfiguration('log_level')],
            parameters=[{
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'drone_id': LaunchConfiguration('drone_id'),
                'drone_ns_prefix': LaunchConfiguration('drone_ns_prefix'),
                'target_x': LaunchConfiguration('target_x'),
                'target_y': LaunchConfiguration('target_y'),
                'target_z': LaunchConfiguration('target_z'),
                'target_yaw': LaunchConfiguration('target_yaw'),
                'rate_hz': LaunchConfiguration('rate_hz'),
                'frame_id': LaunchConfiguration('frame_id'),
            }],
        ),
    ])
