#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    params_file = LaunchConfiguration('params_file')
    log_level = LaunchConfiguration('log_level')
    use_sim_time = LaunchConfiguration('use_sim_time')

    default_params = PathJoinSubstitution(
        [FindPackageShare('state_manager'), 'params', 'state_manager.yaml']
    )

    state_manager_node = Node(
        package='state_manager',
        executable='state_manager_node',
        name='state_manager_node',
        output='screen',
        arguments=['--ros-args', '--log-level', log_level],
        parameters=[params_file, {'use_sim_time': use_sim_time}],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'log_level',
            default_value='info',
            description='Logging level for the state manager node.',
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation clock if true.',
        ),
        DeclareLaunchArgument(
            'params_file',
            default_value=default_params,
            description='Path to the state manager YAML parameter file.',
        ),
        state_manager_node,
    ])
