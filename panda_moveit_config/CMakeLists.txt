cmake_minimum_required(VERSION 3.10.2)
project(panda_moveit_config)
find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(moveit REQUIRED)

install(DIRECTORY launch DESTINATION share/${PROJECT_NAME})
install(DIRECTORY config DESTINATION share/${PROJECT_NAME})
install(FILES .setup_assistant DESTINATION share/${PROJECT_NAME})

# Install Python executables
install(PROGRAMS
  scripts/gripper_to_isaac.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()