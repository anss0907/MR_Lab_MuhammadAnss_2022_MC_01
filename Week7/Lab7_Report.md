# Lab Manual 7: Autonomous Navigation with Nav2 and Multi-Waypoint Mission Planning

**Course:** MCT-454L Mobile Robotics  
**Student:** Muhammad Anss  
**Date:** April 28, 2026

---

## Step 1: Launch Gazebo Simulation

The TurtleBot3 Burger was launched in the `turtlebot3_world` Gazebo environment using:

```
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

The robot spawned at the origin (0, 0, 0) in the same world used during Lab 5 for SLAM mapping.

## Step 2: Launch Nav2 with Saved Map

The Nav2 navigation stack was launched using the saved map from Lab 5:

```
ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True map:=$HOME/MR_Lab_MuhammadAnss/Week5/maps/my_map.yaml
```

This started the Map Server, AMCL localization, Planner Server, Controller Server, BT Navigator, and opened RViz with Nav2 visualization panels.

## Step 3: Set Initial Robot Pose in RViz

The initial pose was set using the **2D Pose Estimate** button in RViz at the robot's spawn location near the origin. After setting the pose, the AMCL particle cloud converged and the laser scan aligned with the map walls. Teleop was briefly used to help AMCL refine its localization estimate.

---

## Task 1: Single Goal Navigation

Three single navigation goals were sent using the **Nav2 Goal** button in RViz.

| Goal # | Start Pose (x, y) | End Pose (x, y) | Orientation (z, w) | Result |
|--------|--------------------|------------------|---------------------|--------|
| 1 | (0.0171, 0.0318) | (1.4513, 0.9929) | (-0.0075, 1.0000) | ✅ Robot reached the goal successfully following a smooth planned path. |
| 2 | (1.4513, 0.9929) | (2.5944, 1.0477) | (-0.7189, 0.6952) | ✅ Robot reached the goal. The planner computed a clear global path and the controller followed it accurately. |
| 3 | (2.5944, 1.0477) | (2.4980, -0.0532) | (-0.0075, 1.0000) | ✅ Robot navigated successfully. The local costmap updated in real time as the robot moved through narrow passages. |

**Observation:** When a goal was set outside the map boundaries (beyond the walls), the planner could not compute a valid path and the goal was rejected. This is expected because the global costmap marks areas outside the mapped region as unknown or lethal, preventing the planner from generating a feasible trajectory.

The robot's estimated pose was verified using:
```
ros2 topic echo /amcl_pose
```

---

## Task 2: Multi-Waypoint Mission

### Waypoint Table

The following 5 waypoints were defined within the map and used for the multi-waypoint navigation mission:

| Waypoint # | X (m) | Y (m) | Z (m) | Orientation Z | Orientation W | Description |
|------------|-------|-------|-------|---------------|---------------|-------------|
| 1 | 1.4513 | 0.9929 | 0.0 | -0.0075 | 1.0000 | Upper corridor entrance |
| 2 | 2.5944 | 1.0477 | 0.0 | -0.7189 | 0.6952 | Mid-upper corridor, facing south |
| 3 | 2.4980 | -0.0532 | 0.0 | -0.0075 | 1.0000 | Center of map, facing east |
| 4 | 3.7521 | -0.0561 | 0.0 | 0.6965 | 0.7176 | Right side of map, facing north |
| 5 | 3.7535 | 1.1022 | 0.0 | 0.7777 | 0.6287 | Upper-right corner, facing northwest |

The `waypoint_navigator_Task2` node was executed using:
```
ros2 run lab7_nav waypoint_navigator_Task2
```

The robot successfully navigated through all 5 waypoints in sequence. The global path updated at each waypoint as a new segment was planned. Screenshots of the robot's position at each waypoint were captured in RViz.

### Source Code

The `waypoint_navigator_Task2.py` node uses the Nav2 `FollowWaypoints` action client. It sends all 5 hardcoded waypoints to the action server and logs feedback as the robot progresses through each waypoint.

---

## Task 3: Dynamic Waypoint Injection

The `waypoint_navigator_Task3.py` node was extended to accept waypoints from command-line arguments. Each group of three values represents `x`, `y`, and `orientation_w` for one waypoint.

**Example usage:**
```
ros2 run lab7_nav waypoint_navigator_Task3 -- 0.5 0.0 1.0 1.0 0.5 1.0 0.0 0.0 1.0
```

If no arguments are provided, the node falls back to the same 5 hardcoded waypoints used in Task 2. The arguments are parsed inside `main()` and the waypoints list is built dynamically.

---

## Task 4: Costmap Observation

### Costmap Topic Names

| Costmap | Topic Name |
|---------|------------|
| **Global Costmap** | `/global_costmap/costmap` |
| **Local Costmap** | `/local_costmap/costmap` |

### Global vs. Local Costmap — Differences

| Aspect | Global Costmap | Local Costmap |
|--------|---------------|--------------|
| **Purpose** | Used by the **global planner** to compute the full path from the robot's current position to the goal across the entire map. | Used by the **local controller (DWB)** to avoid nearby obstacles and follow the planned path in real time. |
| **Scope** | Covers the **entire static map** loaded from the YAML/PGM file. | A **rolling window** centered on the robot (typically 3m × 3m), continuously updating. |
| **Data Source** | Static occupancy grid from the map server + inflation layer. | Live LiDAR sensor data + inflation layer, detecting dynamic obstacles. |
| **Update Rate** | Updated infrequently; primarily reflects the pre-built map. | Updated continuously at the sensor rate to react to new obstacles. |

**Observation:** When the robot approached an obstacle, the local costmap visibly inflated around it, creating a buffer zone. The inflation radius prevents the robot from planning trajectories too close to walls or objects, ensuring safe navigation clearance.

---

## Task 5: Navigation Recovery Behaviors

### Observed Behavior

When a dynamic obstacle (box model) was placed directly in the robot's planned path during navigation, the following recovery sequence was observed:

1. **Detection:** The local costmap immediately detected the new obstacle through the LiDAR sensor data and inflated around it.
2. **Path Invalidation:** The controller recognized that the current local trajectory was blocked and could no longer be followed.
3. **Recovery Action — Retract/Backup:** The robot first backed up slightly to create clearance from the obstacle.
4. **Recovery Action — Stop and Wait:** The robot paused briefly to allow the costmaps to fully update with the new obstacle data.
5. **Replanning:** The global planner computed a **new global path** that routes around the obstacle.
6. **Resumed Navigation:** The controller then followed the new path to reach the original goal.

### Recovery Behavior Server

The recovery behaviors are managed by the **`behavior_server`** node (previously called `recoveries_server` in older Nav2 versions). This node provides three key recovery plugins:

- **`spin`** — Rotates the robot in place to clear out false positive obstacles in the costmap.
- **`backup`** — Drives the robot backwards to create clearance from a blocking obstacle.
- **`wait`** — Pauses navigation to allow dynamic obstacles to potentially clear.

In the `rqt_graph`, the `behavior_server` node is connected to the `/cmd_vel` topic (to command recovery motions) and communicates with the `bt_navigator` through the behavior tree action interface. The BT Navigator's default behavior tree (`navigate_w_replanning_and_recovery.xml`) orchestrates when to invoke recovery behaviors versus when to replan.

---

## Step 6: RViz Visualization

The following display plugins were verified active in RViz during navigation:

| Plugin | Topic | Description |
|--------|-------|-------------|
| Map | `/map` | The loaded occupancy grid from the Map Server |
| Global Costmap | `/global_costmap/costmap` | Inflation layers and obstacle data for the global planner |
| Local Costmap | `/local_costmap/costmap` | Rolling local costmap for the DWB controller |
| Global Path | `/plan` | The planned global trajectory |
| Local Path | `/local_plan` | The local trajectory being followed |
| AMCL Particle Cloud | `/particle_cloud` | Localization uncertainty visualization |
| TF | — | Coordinate frame relationships (map → odom → base_footprint) |
| Odometry | `/odom` | Real-time odometry arrows |
| LaserScan | `/scan` | Live LiDAR data for localization validation |

The Fixed Frame was set to `map` in RViz Global Options to align all data in the world reference frame.

---

## Conclusion

This lab demonstrated the complete autonomous navigation pipeline in ROS 2 using the Nav2 stack with TurtleBot3 in Gazebo simulation. The key learning outcomes include:

1. **Map-Based Navigation:** We successfully loaded the occupancy grid map created in Lab 5 and used it as the foundation for autonomous navigation, demonstrating the practical connection between SLAM (mapping) and navigation (path planning).

2. **AMCL Localization:** The Adaptive Monte Carlo Localization particle filter was used to estimate the robot's pose on the known map. Setting a good initial pose estimate was critical — poor initialization led to misaligned laser scans and navigation failures.

3. **Path Planning and Control:** The Nav2 Planner Server (NavFn) computed collision-free global paths, while the DWB Controller followed these paths locally with real-time obstacle avoidance through the local costmap.

4. **Multi-Waypoint Missions:** We implemented waypoint-based mission planning using the `FollowWaypoints` action server, successfully sending the robot through 5 sequential waypoints both with hardcoded and dynamically injected coordinates.

5. **Recovery Behaviors:** When dynamic obstacles were introduced, Nav2's behavior tree-based recovery system demonstrated robust handling — the robot backed up, waited, and replanned a new path around the obstacle.

### Comparison: Lab 5 (SLAM) vs. Lab 7 (Navigation)

| Aspect | Lab 5 — SLAM | Lab 7 — Navigation |
|--------|-------------|-------------------|
| **Goal** | Build a map of an unknown environment | Navigate autonomously using a known map |
| **Localization** | Cartographer (simultaneous mapping + localization) | AMCL (localization on a pre-built map) |
| **Map** | Being created incrementally as the robot explores | Pre-loaded static map from Lab 5 |
| **Control** | Manual teleoperation to drive the robot | Autonomous path planning and trajectory following |
| **Key Challenge** | Ensuring complete coverage and loop closure | Accurate initial pose estimation and dynamic obstacle handling |
| **Output** | Saved map files (PGM + YAML) | Completed navigation missions with recovery behaviors |

In SLAM (Lab 5), the robot had no prior knowledge of the environment and had to build a map while simultaneously localizing itself — a computationally expensive process requiring manual teleoperation. In Navigation (Lab 7), the robot leveraged the pre-built map for efficient autonomous movement, with the Nav2 stack handling all planning, control, and recovery automatically. Together, these two labs form the complete autonomy pipeline: first map, then navigate.

---

## Commands Used

```bash
# Step 1: Launch Gazebo
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

# Step 2: Launch Nav2 with saved map
ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True map:=$HOME/MR_Lab_MuhammadAnss/Week5/maps/my_map.yaml

# Teleop for localization refinement
ros2 run turtlebot3_teleop teleop_keyboard

# Single goal via command line
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "{pose: {header: {frame_id: 'map'}, pose: {position: {x: 1.0, y: 0.5, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}}}"

# Goal recorder
ros2 run lab7_nav goal_recorder

# Task 2: Multi-waypoint navigation
ros2 run lab7_nav waypoint_navigator_Task2

# Task 3: Dynamic waypoint injection
ros2 run lab7_nav waypoint_navigator_Task3 -- 0.5 0.0 1.0 1.0 0.5 1.0 0.0 0.0 1.0
```
