import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import ComposableNodeContainer, Node
from launch_ros.descriptions import ComposableNode
from moveit_configs_utils import MoveItConfigsBuilder

import yaml


def generate_launch_description():

    # Command-line arguments
    ros2_control_hardware_type = DeclareLaunchArgument(
        'ros2_control_hardware_type',
        default_value='isaac',
        description=(
            'ROS2 control hardware interface type to use for the launch file -- '
            'possible values: [mock_components, isaac]'
        )
    )

    moveit_config = (
        MoveItConfigsBuilder('panda')
        .robot_description(
            file_path='config/panda.urdf.xacro',
            mappings={
                'ros2_control_hardware_type': LaunchConfiguration(
                    'ros2_control_hardware_type'
                )
            },
        )
        .robot_description_semantic(file_path='config/panda.srdf')
        .trajectory_execution(file_path='config/gripper_moveit_controllers.yaml')
        .planning_pipelines(pipelines=['ompl', 'pilz_industrial_motion_planner'])
        .to_moveit_configs()
    )

    # Configure MoveIt to use the cuMotion planning pipeline.
    cumotion_config_file_path = os.path.join(
        get_package_share_directory('isaac_ros_cumotion_moveit'),
        'config',
        'isaac_ros_cumotion_planning.yaml'
    )
    with open(cumotion_config_file_path) as cumotion_config_file:
        cumotion_config = yaml.safe_load(cumotion_config_file)
    moveit_config.planning_pipelines['planning_pipelines'] = ['isaac_ros_cumotion']
    moveit_config.planning_pipelines['default_planning_pipeline'] = 'isaac_ros_cumotion'
    moveit_config.planning_pipelines['isaac_ros_cumotion'] = cumotion_config

    # The current Franka asset in Isaac Sim 2023.1.1 tends to drift slightly from commanded joint
    # positions, which prevents trajectory execution if the drift exceeds `allowed_start_tolerance`
    # for any joint; the default tolerance is 0.01 radians.  This is more likely to occur if the
    # robot hasn't fully settled when the trajectory is computed or if significant time has
    # elapsed between trajectory computation and execution. For this simulation use case,
    # there's little harm in disabling this check by setting `allowed_start_tolerance` to 0.
    moveit_config.trajectory_execution['trajectory_execution']['allowed_start_tolerance'] = 0.0

    # Start the actual move_group node/action server
    move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[moveit_config.to_dict()],
        arguments=['--ros-args', '--log-level', 'info'],
    )

    # Add cuMotion components as composable nodes in a shared container.
    xrdf_path = os.path.join(
        get_package_share_directory('isaac_ros_cumotion_robot_description'),
        'xrdf', 'franka.xrdf'
    )
    urdf_path = os.path.join(
        get_package_share_directory('panda_description'),
        'urdf', 'panda.urdf'
    )
    cumotion_planner_node = ComposableNode(
        name='cumotion_planner',
        package='isaac_ros_cumotion',
        plugin='nvidia::isaac_ros::cumotion::CumotionPlanner',
        parameters=[
            {
                'urdf_file_path': urdf_path,
                'xrdf_file_path': xrdf_path,
            }
        ],
    )

    static_planning_scene_server = ComposableNode(
        name='static_planning_scene_server',
        package='isaac_ros_cumotion',
        plugin='nvidia::isaac_ros::cumotion::StaticPlanningSceneServer',
        parameters=[{
            'moveit_collision_objects_scene_file': '',
        }],
    )

    cumotion_container = ComposableNodeContainer(
        name='cumotion_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container_mt',
        composable_node_descriptions=[
            static_planning_scene_server,
            cumotion_planner_node,
        ],
        output='screen',
        emulate_tty=True,
    )

    # RViz
    rviz_config_file = os.path.join(
        get_package_share_directory('isaac_ros_cumotion_examples'),
        'rviz',
        'franka_moveit_config.rviz',
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='log',
        arguments=['-d', rviz_config_file],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.planning_pipelines,
            moveit_config.joint_limits,
        ],
    )

    # Publish TF
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[moveit_config.robot_description],
    )

    # ros2_control using FakeSystem as hardware
    ros2_controllers_path = os.path.join(
        get_package_share_directory('panda_moveit_config'),
        'config',
        'ros2_controllers.yaml',
    )
    ros2_control_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[ros2_controllers_path],
        remappings=[
            ('/controller_manager/robot_description', '/robot_description'),
        ],
        output='screen',
    )

    joint_state_broadcaster_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '--controller-manager',
            '/controller_manager',
        ],
    )

    panda_arm_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['panda_arm_controller', '-c', '/controller_manager'],
    )

    panda_hand_controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['panda_hand_controller', '-c', '/controller_manager'],
    )

    return LaunchDescription(
        [
            ros2_control_hardware_type,
            rviz_node,
            robot_state_publisher,
            move_group_node,
            ros2_control_node,
            joint_state_broadcaster_spawner,
            panda_arm_controller_spawner,
            panda_hand_controller_spawner,
            cumotion_container,
        ]
    )
