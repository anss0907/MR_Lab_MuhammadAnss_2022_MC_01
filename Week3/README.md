# Week 3 — ROS 2 Lab: Turtlesim Motion Patterns and Go-to-Goal

## Description

This folder contains the Week 3 deliverables for MCT-454L (Mobile Robotics). The lab focused on creating a ROS 2 Python package for `turtlesim`, implementing motion patterns, controlling multiple turtles, and moving a turtle to a target location using ROS 2 topics.

## Package and Nodes

Package: `my_turtle_package`

Implemented nodes:
- `move_patterns_node` — Task 1 (circular + triangular motion)
- `multi_turtle_node` — Task 2 (spawn and control multiple turtles)
- `go_to_goal_node` — Task 3 (move turtle to a specific goal position)

## Commands Used

```bash
# 1) Go to workspace root
cd ~/MR_Lab_MuhammadAnss/ros2_ws

# 2) Build workspace
colcon build

# 3) Source workspace
source install/setup.bash

# 4) Run turtlesim (Terminal 1)
ros2 run turtlesim turtlesim_node

# 5) Run Task 1 node (Terminal 2)
ros2 run my_turtle_package move_patterns_node

# 6) Run Task 2 node (Terminal 2, restart turtlesim first if needed)
ros2 run my_turtle_package multi_turtle_node

# 7) Run Task 3 node (Terminal 2)
ros2 run my_turtle_package go_to_goal_node

# 8) Send a goal pose for Task 3 (Terminal 3)
ros2 topic pub --once /turtle1/goal_pose turtlesim/msg/Pose "{x: 8.0, y: 8.0, theta: 0.0, linear_velocity: 0.0, angular_velocity: 0.0}"
```

## Week 3 Tasks

1. **Task 1 — Circular and Triangular Pattern**  
   Implemented in `move_patterns_node.py`. The turtle first moves in a circular path, then executes triangular motion using timed linear and angular velocity commands.

2. **Task 2 — Spawn Three Turtles with Different Patterns**  
   Implemented in `multi_turtle_node.py`. The node uses `/spawn` service to create additional turtles and publishes velocity commands so turtles follow different behaviors (circle/triangle/square-like phases).

3. **Task 3 — Move Turtle to a Specific Location**  
   Implemented in `go_to_goal_node.py`. The node subscribes to `/turtle1/pose`, accepts goals on `/turtle1/goal_pose`, and applies a proportional controller for heading and distance.

## Output Evidence

- Task 1 output: `Task1_TurtleSim_output.png`
- Task 2 output: `Task2_TurtleSim_output.png`
- Task 3 output: `Task3_TurtleSim_output.png`

## Reflection

This lab strengthened practical ROS 2 skills beyond basic node execution. Building task-specific turtlesim controllers improved understanding of publishers, subscribers, services, and timed control loops. The go-to-goal controller introduced feedback-based motion control and showed how topic-based goal input can be used for simple autonomous navigation behavior.