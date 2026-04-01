#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable, TimerAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    default_params = PathJoinSubstitution(
        [FindPackageShare('skyw_swarm'), 'config', 'formation.yaml']
    )
    default_fastdds = PathJoinSubstitution(
        [FindPackageShare('skyw_swarm'), 'config', 'fastdds.xml']
    )

    params_file = LaunchConfiguration('params_file')
    namespace = LaunchConfiguration('namespace')
    log_level = LaunchConfiguration('log_level')
    use_sim_time = LaunchConfiguration('use_sim_time')
    drone_count = LaunchConfiguration('drone_count')
    start_client = LaunchConfiguration('start_client')
    start_controller = LaunchConfiguration('start_controller')
    client_delay = LaunchConfiguration('client_delay')
    use_fastdds_xml = LaunchConfiguration('use_fastdds_xml')
    fastdds_xml = LaunchConfiguration('fastdds_xml')

    bridge = Node(
        package='skyw_swarm',
        executable='px4_pose_bridge.py',
        namespace=namespace,
        name='px4_pose_bridge',
        output='screen',
        arguments=['--ros-args', '--log-level', log_level],
        parameters=[params_file, {'drone_count': drone_count, 'use_sim_time': use_sim_time}],
    )

    server = Node(
        package='skyw_swarm',
        executable='formation_server.py',
        namespace=namespace,
        name='formation_server',
        output='screen',
        arguments=['--ros-args', '--log-level', log_level],
        parameters=[params_file, {'drone_count': drone_count, 'use_sim_time': use_sim_time}],
    )

    client = Node(
        package='skyw_swarm',
        executable='formation_client.py',
        namespace=namespace,
        name='formation_client',
        output='screen',
        arguments=['--ros-args', '--log-level', log_level],
        parameters=[params_file, {'drone_count': drone_count, 'use_sim_time': use_sim_time}],
        condition=IfCondition(start_client),
    )

    controller = Node(
        package='skyw_swarm',
        executable='swarm_controller.py',
        namespace=namespace,
        name='swarm_controller',
        output='screen',
        arguments=['--ros-args', '--log-level', log_level],
        parameters=[params_file, {'drone_count': drone_count, 'use_sim_time': use_sim_time}],
        condition=IfCondition(start_controller),
    )

    delayed_client = TimerAction(period=client_delay, actions=[client])

    return LaunchDescription([
        DeclareLaunchArgument(
            'namespace',
            default_value='',
            description='Namespace for swarm nodes (empty for global)',
        ),
        DeclareLaunchArgument(
            'log_level',
            default_value='info',
            description='Logging level for swarm nodes',
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation clock if true',
        ),
        DeclareLaunchArgument(
            'params_file',
            default_value=default_params,
            description='Path to YAML parameter file containing formation_server and formation_client params',
        ),
        DeclareLaunchArgument(
            'drone_count',
            default_value='3',
            description='Override drone_count for bridge/server/client',
        ),
        DeclareLaunchArgument(
            'start_client',
            default_value='false',
            description='Whether to auto-launch formation_client',
        ),
        DeclareLaunchArgument(
            'start_controller',
            default_value='true',
            description='Whether to launch swarm_controller (param-driven)',
        ),
        DeclareLaunchArgument(
            'client_delay',
            default_value='2.0',
            description='Delay in seconds before launching formation_client',
        ),
        DeclareLaunchArgument(
            'use_fastdds_xml',
            default_value='false',
            description='Set Fast DDS XML env vars for all launched nodes',
        ),
        DeclareLaunchArgument(
            'fastdds_xml',
            default_value=default_fastdds,
            description='Path to Fast DDS XML profile file',
        ),
        SetEnvironmentVariable('RMW_IMPLEMENTATION', 'rmw_fastrtps_cpp'),
        SetEnvironmentVariable('RMW_FASTRTPS_USE_QOS_FROM_XML', '1', condition=IfCondition(use_fastdds_xml)),
        SetEnvironmentVariable('FASTDDS_DEFAULT_PROFILES_FILE', fastdds_xml, condition=IfCondition(use_fastdds_xml)),
        bridge,
        server,
        controller,
        delayed_client,
    ])
