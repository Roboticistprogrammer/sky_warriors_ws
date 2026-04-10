#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('drone_id', default_value='1'),
        DeclareLaunchArgument('px4_ns_prefix', default_value='/px4_'),
        DeclareLaunchArgument('drone_ns_prefix', default_value='/drone'),
        DeclareLaunchArgument('offboard_rate_hz', default_value='20.0'),
        DeclareLaunchArgument('setpoint_timeout_s', default_value='1.0'),
        DeclareLaunchArgument('auto_arm', default_value='true'),
        DeclareLaunchArgument('auto_offboard', default_value='true'),
        DeclareLaunchArgument('target_system_start', default_value='1'),
        DeclareLaunchArgument('target_component', default_value='1'),
        DeclareLaunchArgument('fallback_enable', default_value='true'),
        DeclareLaunchArgument('fallback_takeoff_x', default_value='0.0'),
        DeclareLaunchArgument('fallback_takeoff_y', default_value='0.0'),
        DeclareLaunchArgument('fallback_takeoff_z', default_value='-2.5'),
        DeclareLaunchArgument('fallback_takeoff_hold_s', default_value='3.0'),
        DeclareLaunchArgument('fallback_target_x', default_value='5.0'),
        DeclareLaunchArgument('fallback_target_y', default_value='0.0'),
        DeclareLaunchArgument('fallback_target_z', default_value='-1.0'),
        DeclareLaunchArgument('fallback_target_yaw', default_value='1.57'),
        DeclareLaunchArgument('log_level', default_value='info'),
        Node(
            package='skyw_swarm',
            executable='px4_offboard_bridge.py',
            name='px4_offboard_bridge',
            output='screen',
            arguments=['--ros-args', '--log-level', LaunchConfiguration('log_level')],
            parameters=[{
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'drone_count': 1,
                'offboard_rate_hz': LaunchConfiguration('offboard_rate_hz'),
                'setpoint_timeout_s': LaunchConfiguration('setpoint_timeout_s'),
                'auto_arm': LaunchConfiguration('auto_arm'),
                'auto_offboard': LaunchConfiguration('auto_offboard'),
                'target_system_start': LaunchConfiguration('target_system_start'),
                'target_component': LaunchConfiguration('target_component'),
                'px4_ns_prefix': LaunchConfiguration('px4_ns_prefix'),
                'drone_ns_prefix': LaunchConfiguration('drone_ns_prefix'),
                'fallback_enable': LaunchConfiguration('fallback_enable'),
                'fallback_takeoff_x': LaunchConfiguration('fallback_takeoff_x'),
                'fallback_takeoff_y': LaunchConfiguration('fallback_takeoff_y'),
                'fallback_takeoff_z': LaunchConfiguration('fallback_takeoff_z'),
                'fallback_takeoff_hold_s': LaunchConfiguration('fallback_takeoff_hold_s'),
                'fallback_target_x': LaunchConfiguration('fallback_target_x'),
                'fallback_target_y': LaunchConfiguration('fallback_target_y'),
                'fallback_target_z': LaunchConfiguration('fallback_target_z'),
                'fallback_target_yaw': LaunchConfiguration('fallback_target_yaw'),
            }],
        ),
    ])
