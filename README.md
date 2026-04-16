# panda_robot_sim

Panda robot under NVIDIA isaac sim and ROS2.

------

## System Requirements

- OS : Ubuntu 24.04
- CPU : Intel Core i7 (7th Generation) / AMD Ryzen 5
- Cores : 4
- RAM : 32 GB
- Storage : 50GB SSD
- GPU : GeForce RTX 4080
- VRAM : 16GB
- Driver : Linux: 580.65.06

------

## Built with

- ROS Jazzy under Ubuntu 24.04 LTS

------

## Getting Started

### Installation

- Installation NVIDIA Isaac Sim

    - NVIDIA Isaac Sim Install - https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/download.html

- Installation ros package.

    ``` $ sudo apt install ros-jazzy-moveit```

### Run

- Running panda robot using moveit2 planning.

``` bash
$ ros2 launch panda_moveit_config isaac_demo.launch.py
```

- Manual control panda robot using servo control

``` bash
$ ros2 launch panda_teleop panda_teleop.launch.py
```

``` bash
$ ros2 run panda_teleop panda_teleop
```

------

## Reference:

[1]. moveit2 tutorial. https://moveit.picknik.ai/main/doc/tutorials/tutorials.html

[2]. Isaacsim moveit tutorial. https://docs.isaacsim.omniverse.nvidia.com/5.1.0/ros2_tutorials/tutorial_ros2_moveit.html

[3]. Isaac ROS. https://nvidia-isaac-ros.github.io/index.html

------

This repository is for your reference only. copying, patent application, academic journals are strictly prohibited.

Copyright © 2026 ZM Robotics Software Laboratory.
