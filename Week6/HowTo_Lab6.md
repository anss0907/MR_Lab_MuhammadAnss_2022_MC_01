# Lab 6: LiDAR-Based Reactive Navigation — How-To Guide

## 1. Pre-Lab Setup

### Terminal 1 — Launch Gazebo Simulation
```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

### Terminal 2 — Verify LiDAR topic is active
```bash
ros2 topic list | grep scan
ros2 topic echo /scan --once
```

### (Optional) Terminal 3 — Open RViz to visualize LaserScan
```bash
ros2 run rviz2 rviz2
```
In RViz: Add → By topic → `/scan` → LaserScan. Set Fixed Frame to `odom`.

---

## 2. Build the Package

```bash
cd ~/MR_Lab_MuhammadAnss/ros2_ws
colcon build --packages-select lidar_nav_lab6
source install/setup.bash
```

---

## 3. Run Each Task

The node has a `mode` parameter to switch between tasks:

| Mode          | Task | Behaviour                              |
|---------------|------|----------------------------------------|
| `scan_only`   | 1    | Print front/left/right distances only  |
| `stop`        | 2    | Move forward, stop at obstacle         |
| `avoid`       | 3    | Avoid obstacles, turn to clearer side  |
| `wall_follow` | 4    | Follow right wall with P-controller    |
| `full`        | 5    | Combined: avoid + wall-follow + cruise |

### Task 1 — Scan Processing (just observe distances)
```bash
ros2 run lidar_nav_lab6 lidar_navigator --ros-args -p mode:=scan_only
```

### Task 2 — Stop-on-Obstacle
```bash
ros2 run lidar_nav_lab6 lidar_navigator --ros-args -p mode:=stop
```

### Task 3 — Obstacle Avoidance
```bash
ros2 run lidar_nav_lab6 lidar_navigator --ros-args -p mode:=avoid
```

### Task 4 — Wall Following
```bash
ros2 run lidar_nav_lab6 lidar_navigator --ros-args -p mode:=wall_follow
```

### Task 5 — Behaviour Sequencing (default)
```bash
ros2 run lidar_nav_lab6 lidar_navigator
```

---

## 4. Monitoring & Debugging

### Watch velocity commands being published
```bash
ros2 topic echo /cmd_vel
```

### View the ROS 2 computation graph (for deliverable screenshot)
```bash
rqt_graph
```
This will show `/lidar_navigator` subscribing to `/scan` and publishing to `/cmd_vel`.

---

## 5. Tuning Thresholds

You can edit these constants at the top of `lidar_navigator.py`:

| Parameter         | Default | Effect                                |
|-------------------|---------|---------------------------------------|
| `FRONT_THRESHOLD` | 0.5 m   | Distance to trigger stop/avoidance    |
| `SIDE_THRESHOLD`  | 0.5 m   | Desired wall-follow distance          |
| `LINEAR_SPEED`    | 0.15    | Forward speed (m/s)                   |
| `ANGULAR_SPEED`   | 0.5     | Turning speed (rad/s)                 |
| `WALL_KP`         | 1.5     | Proportional gain for wall following  |

After editing, rebuild:
```bash
cd ~/MR_Lab_MuhammadAnss/ros2_ws
colcon build --packages-select lidar_nav_lab6
source install/setup.bash
```

---

## 6. Deliverable Checklist

- [ ] Push package to GitHub
- [ ] Source code with scan processing, region extraction, obstacle avoidance
- [ ] Screenshots of LaserScan in RViz
- [ ] Screenshots of robot navigating in Gazebo
- [ ] Screenshot of `rqt_graph`
- [ ] Demo: robot stops at obstacle (mode: `stop`)
- [ ] Demo: robot avoids obstacle (mode: `avoid`)
- [ ] Demo: robot navigates without collision (mode: `full`)
- [ ] Observations on behaviour, oscillations, threshold effects
- [ ] Brief conclusion
