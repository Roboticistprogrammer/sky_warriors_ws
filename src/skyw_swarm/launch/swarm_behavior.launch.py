#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    default_config = PathJoinSubstitution(
        [FindPackageShare('skyw_swarm'), 'config', 'formation.yaml']
    )

    behavior_config_file = LaunchConfiguration('behavior_config_file')
    namespace = LaunchConfiguration('namespace')
    log_level = LaunchConfiguration('log_level')
    use_sim_time = LaunchConfiguration('use_sim_time')
    drone_count = LaunchConfiguration('drone_count')

    behavior_node = Node(
        package='skyw_swarm',
        executable='swarm_controller.py',
        namespace=namespace,
        name='swarm_behavior',
        output='screen',
        arguments=['--ros-args', '--log-level', log_level],
        parameters=[
            behavior_config_file,
            {'drone_count': drone_count, 'use_sim_time': use_sim_time},
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'behavior_config_file',
            default_value=default_config,
            description='Path to swarm behavior configuration file',
        ),
        DeclareLaunchArgument(
            'namespace',
            default_value='Swarm',
            description='Namespace for swarm behavior node',
        ),
        DeclareLaunchArgument(
            'log_level',
            default_value='info',
            description='Logging level for swarm behavior node',
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation clock if true',
        ),
        DeclareLaunchArgument(
            'drone_count',
            default_value='3',
            description='Override drone_count for the behavior node',
        ),
        behavior_node,
    ])
