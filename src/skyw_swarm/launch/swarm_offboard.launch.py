#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    default_params = PathJoinSubstitution(
        [FindPackageShare('skyw_swarm'), 'config', 'swarm_ids.yaml']
    )

    namespace = LaunchConfiguration('namespace')
    log_level = LaunchConfiguration('log_level')
    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')

    drone_count = LaunchConfiguration('drone_count')
    offboard_rate_hz = LaunchConfiguration('offboard_rate_hz')
    setpoint_timeout_s = LaunchConfiguration('setpoint_timeout_s')
    auto_arm = LaunchConfiguration('auto_arm')
    auto_offboard = LaunchConfiguration('auto_offboard')
    target_system_start = LaunchConfiguration('target_system_start')
    target_component = LaunchConfiguration('target_component')
    px4_ns_prefix = LaunchConfiguration('px4_ns_prefix')
    drone_ns_prefix = LaunchConfiguration('drone_ns_prefix')

    offboard_node = Node(
        package='skyw_swarm',
        executable='px4_offboard_bridge.py',
        namespace=namespace,
        name='px4_offboard_bridge',
        output='screen',
        arguments=['--ros-args', '--log-level', log_level],
        parameters=[
            params_file,
            {
                'use_sim_time': use_sim_time,
                'drone_count': drone_count,
                'offboard_rate_hz': offboard_rate_hz,
                'setpoint_timeout_s': setpoint_timeout_s,
                'auto_arm': auto_arm,
                'auto_offboard': auto_offboard,
                'target_system_start': target_system_start,
                'target_component': target_component,
                'px4_ns_prefix': px4_ns_prefix,
                'drone_ns_prefix': drone_ns_prefix,
            },
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'namespace',
            default_value='',
            description='Namespace for the offboard bridge node',
        ),
        DeclareLaunchArgument(
            'log_level',
            default_value='info',
            description='Logging level for the offboard bridge node',
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation clock if true',
        ),
        DeclareLaunchArgument(
            'params_file',
            default_value=default_params,
            description='YAML file with swarm ids and namespace parameters',
        ),
        DeclareLaunchArgument(
            'drone_count',
            default_value='3',
            description='Number of drones to control',
        ),
        DeclareLaunchArgument(
            'offboard_rate_hz',
            default_value='20.0',
            description='Publish rate for offboard setpoints',
        ),
        DeclareLaunchArgument(
            'setpoint_timeout_s',
            default_value='1.0',
            description='Max age for setpoint messages',
        ),
        DeclareLaunchArgument(
            'auto_arm',
            default_value='true',
            description='Automatically arm when offboard starts',
        ),
        DeclareLaunchArgument(
            'auto_offboard',
            default_value='true',
            description='Automatically request offboard mode',
        ),
        DeclareLaunchArgument(
            'target_system_start',
            default_value='1',
            description='First PX4 MAVLink system id',
        ),
        DeclareLaunchArgument(
            'target_component',
            default_value='1',
            description='PX4 MAVLink component id',
        ),
        DeclareLaunchArgument(
            'px4_ns_prefix',
            default_value='/px4_',
            description='PX4 namespace prefix (e.g., /px4_)',
        ),
        DeclareLaunchArgument(
            'drone_ns_prefix',
            default_value='/drone',
            description='Setpoint namespace prefix (e.g., /drone)',
        ),
        offboard_node,
    ])
