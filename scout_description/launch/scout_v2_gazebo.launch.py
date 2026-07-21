from launch import LaunchDescription
from launch.actions import (
    AppendEnvironmentVariable,
    DeclareLaunchArgument,
    IncludeLaunchDescription,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    world = LaunchConfiguration("world")
    gui = LaunchConfiguration("gui")
    robot_name = LaunchConfiguration("robot_name")
    x = LaunchConfiguration("x")
    y = LaunchConfiguration("y")
    z = LaunchConfiguration("z")
    yaw = LaunchConfiguration("yaw")

    xacro_file = PathJoinSubstitution(
        [
            FindPackageShare("scout_description"),
            "urdf",
            "scout_v2",
            "scout_v2_gazebo.xacro",
        ]
    )

    gazebo_resource_path = AppendEnvironmentVariable(
        "GZ_SIM_RESOURCE_PATH",
        PathJoinSubstitution([FindPackageShare("scout_description"), ".."]),
    )

    robot_description = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            xacro_file,
        ]
    )

    gz_sim_launch = PythonLaunchDescriptionSource(
        PathJoinSubstitution(
            [FindPackageShare("ros_gz_sim"), "launch", "gz_sim.launch.py"]
        )
    )

    gazebo_with_gui = IncludeLaunchDescription(
        gz_sim_launch,
        launch_arguments={"gz_args": ["-r -v 4 ", world]}.items(),
        condition=IfCondition(gui),
    )

    gazebo_headless = IncludeLaunchDescription(
        gz_sim_launch,
        launch_arguments={"gz_args": ["-r -s -v 4 ", world]}.items(),
        condition=UnlessCondition(gui),
    )

    state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[
            {
                "use_sim_time": use_sim_time,
                "robot_description": robot_description,
            }
        ],
    )

    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-name",
            robot_name,
            "-topic",
            "robot_description",
            "-x",
            x,
            "-y",
            y,
            "-z",
            z,
            "-Y",
            yaw,
        ],
        output="screen",
    )

    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist",
            "/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry",
            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
        ],
        output="screen",
    )

    return LaunchDescription(
        [

            DeclareLaunchArgument(
                "use_sim_time",
                default_value="true",
                description="Use Gazebo simulation clock.",
            ),
            DeclareLaunchArgument(
                "world",
                default_value="empty.sdf",
                description="Gazebo world file or resource name.",
            ),
            DeclareLaunchArgument(
                "gui",
                default_value="true",
                description="Start Gazebo with the GUI. Set false for server only.",
            ),
            DeclareLaunchArgument(
                "robot_name",
                default_value="scout_v2",
                description="Name of the spawned Gazebo model.",
            ),
            DeclareLaunchArgument("x", default_value="0.0", description="Spawn X pose."),
            DeclareLaunchArgument("y", default_value="0.0", description="Spawn Y pose."),
            DeclareLaunchArgument("z", default_value="0.25", description="Spawn Z pose."),
            DeclareLaunchArgument(
                "yaw", default_value="0.0", description="Spawn yaw in radians."
            ),
            gazebo_resource_path,
            gazebo_with_gui,
            gazebo_headless,
            state_publisher,
            spawn_robot,
            bridge,
        ]
    )
