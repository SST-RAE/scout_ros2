from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import FindExecutable


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    port_name = LaunchConfiguration('port_name')
    lidar_x = LaunchConfiguration('lidar_x')
    lidar_y = LaunchConfiguration('lidar_y')
    lidar_z = LaunchConfiguration('lidar_z')
    lidar_roll = LaunchConfiguration('lidar_roll')
    lidar_pitch = LaunchConfiguration('lidar_pitch')
    lidar_yaw = LaunchConfiguration('lidar_yaw')
    nav2_params_file = LaunchConfiguration('nav2_params_file')
    rviz_config = LaunchConfiguration('rviz_config')
    start_rviz = LaunchConfiguration('start_rviz')
    linear_speed = LaunchConfiguration('linear_speed')
    circle_radius = LaunchConfiguration('circle_radius')

    robot_description = Command([
        PathJoinSubstitution([FindExecutable(name='xacro')]),
        ' ',
        PathJoinSubstitution([
            FindPackageShare('scout_description'),
            'urdf',
            'scout_v2',
            'scout_v2.xacro',
        ]),
    ])

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('port_name', default_value='can0'),
        DeclareLaunchArgument('lidar_x', default_value='0.20'),
        DeclareLaunchArgument('lidar_y', default_value='0.0'),
        DeclareLaunchArgument('lidar_z', default_value='0.20'),
        DeclareLaunchArgument('lidar_roll', default_value='0.0'),
        DeclareLaunchArgument('lidar_pitch', default_value='0.0'),
        DeclareLaunchArgument('lidar_yaw', default_value='0.0'),
        DeclareLaunchArgument('linear_speed', default_value='0.3'),
        DeclareLaunchArgument('circle_radius', default_value='2.0'),
        DeclareLaunchArgument(
            'nav2_params_file',
            default_value=PathJoinSubstitution([
                FindPackageShare('scout_nav2_bringup'),
                'config',
                'nav2_circle_params.yaml',
            ]),
        ),
        DeclareLaunchArgument(
            'rviz_config',
            default_value=PathJoinSubstitution([
                FindPackageShare('scout_nav2_bringup'),
                'rviz',
                'scout_v2_mapping.rviz',
            ]),
        ),
        DeclareLaunchArgument('start_rviz', default_value='true'),

        Node(
            package='scout_base',
            executable='scout_base_node',
            output='screen',
            emulate_tty=True,
            parameters=[{
                'use_sim_time': use_sim_time,
                'port_name': port_name,
                'odom_frame': 'odom',
                'base_frame': 'base_link',
                'odom_topic_name': 'odom',
                'is_scout_mini': False,
                'is_omni_wheel': False,
                'auto_reconnect': True,
                'simulated_robot': False,
                'control_rate': 50,
            }],
        ),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'robot_description': robot_description,
            }],
        ),

        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'rate': 50,
            }],
        ),

        Node(
            name='rplidar_composition',
            package='rplidar_ros',
            executable='rplidar_composition',
            output='screen',
            parameters=[{
                'serial_port': '/dev/ttyUSB1',
                'serial_baudrate': 256000,
                'frame_id': 'laser',
                'inverted': False,
                'angle_compensate': True,
                'scan_mode': 'Sensitivity',
            }],
        ),

        Node(
            package='nav2_costmap_2d',
            executable='nav2_costmap_2d',
            name='local_costmap',
            output='screen',
            parameters=[nav2_params_file],
        ),

        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=[nav2_params_file],
        ),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager',
            output='screen',
            parameters=[nav2_params_file],
        ),

        Node(
            package='scout_nav2_bringup',
            executable='circle_driver_node.py',
            name='circle_driver_node',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'linear_speed': linear_speed,
                'circle_radius': circle_radius,
            }],
        ),

        Node(
            condition=IfCondition(start_rviz),
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': use_sim_time}],
        ),
    ])
