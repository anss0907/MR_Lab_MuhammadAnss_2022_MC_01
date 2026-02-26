# Week 1 — ROS 2 Lab: Workspace Setup and First Package

## Description

This folder contains the deliverables for Week 1 of the Mobile Robotics Lab (MCT-454L). The objective was to set up a ROS 2 development environment, create a Python package, write a simple node, and run it using `ros2 run`.

## Commands Used

```bash
# Verify ROS 2 installation
echo $ROS_DISTRO

# Create workspace
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws

# Create package
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python my_first_pkg

# Build workspace
cd ~/ros2_ws
colcon build

# Source workspace
source install/setup.bash

# Verify package is visible
ros2 pkg list | grep my_first_pkg

# Run the basic node
ros2 run my_first_pkg simple_node

# Run Task 1 — Custom message
ros2 run my_first_pkg w1_task1_node

# Run Task 2 — Counter
ros2 run my_first_pkg w1_task2_node

# Run Task 3 — Parameter (without setting it)
ros2 run my_first_pkg w1_task3_node

# Run Task 3 — Parameter (with name set)
ros2 run my_first_pkg w1_task3_node --ros-args -p student_name:="Muhammad Anss"
```

## Experiment Tasks

- **Task 1** (`w1_task1_node.py`): Changed the log message to print `Welcome to Mobile Robotics Lab`.
- **Task 2** (`w1_task2_node.py`): Added a persistent counter that increments on each run and prints `Run count: N`.
- **Task 3** (`w1_task3_node.py`): Added a `student_name` ROS parameter. Prints the name if set, otherwise prints `student_name not set`.

## Problems Faced and Solutions

1. **`apt` lock blocking terminal**: Another `apt` process was running in the background and held the dpkg lock. Waited for it to finish before proceeding.
2. **Setuptools SCM warning during build**: `colcon build` showed a harmless stderr warning about `setuptools_scm` and git file listing. This did not affect the build and was ignored.

## Reflection

This lab was a solid introduction to ROS 2 from the ground up. Setting up the workspace with `colcon build` and understanding the folder structure (`src/`, `build/`, `install/`, `log/`) gave me a clear picture of how ROS 2 organizes code and build artifacts. Creating a Python package using `ros2 pkg create` was straightforward, but understanding the role of `setup.py` — especially the `entry_points` section — was the key takeaway. Without correctly registering an entry point, `ros2 run` simply cannot find your node. Writing the `simple_node.py` and seeing the log output confirmed that the pipeline from code to execution works correctly. The experiment tasks pushed me to explore parameters and file-based persistence, which will be useful for more complex nodes in future weeks. Overall, this lab built a strong foundation for working with ROS 2 going forward.
