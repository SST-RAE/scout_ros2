cmake_minimum_required(VERSION 3.5)
project(scout_nav2_bringup)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch config rviz
  DESTINATION share/${PROJECT_NAME}/
)

install(PROGRAMS
  scripts/circle_driver_node.py
  DESTINATION lib/${PROJECT_NAME}/
)

ament_package()
