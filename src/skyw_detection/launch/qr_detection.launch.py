from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    # Declare launch arguments
    camera_topic_arg = DeclareLaunchArgument(
        'camera_topic',
        default_value='camera/image_raw',
        description='Camera image topic name'
    )
    
    camera_info_topic_arg = DeclareLaunchArgument(
        'camera_info_topic',
        default_value='camera/camera_info',
        description='Camera info topic name'
    )
    
    enable_visualization_arg = DeclareLaunchArgument(
        'enable_visualization',
        default_value='true',
        description='Enable QR code visualization'
    )    

    # QR Detector Node
    qr_detector_node = Node(
        package='qr_detection',
        executable='qr_detector_node',
        name='qr_detector_node',
        output='screen',
        parameters=[{
            'enable_visualization': LaunchConfiguration('enable_visualization'),
            'qr_size': LaunchConfiguration('qr_size'),
        }],
        remappings=[
            ('camera/image_raw', LaunchConfiguration('camera_topic')),
            ('camera/camera_info', LaunchConfiguration('camera_info_topic')),
        ]
    )

    return LaunchDescription([
        camera_topic_arg,
        camera_info_topic_arg,
        enable_visualization_arg,
        qr_detector_node,
    ])
