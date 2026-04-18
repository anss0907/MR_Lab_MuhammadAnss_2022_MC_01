# MCT-454L Mobile Robotics — Lab 4 Report

**Lab Session 4**: Introduction to ROS 2 Launch, Rosbag, rqt-plot
**Date**: 10 April 2026

---

## 1. Approach

The lab was carried out in the following stages:

1. **Launch file creation** — A ROS 2 Python launch file (`turtlesim_launch.py`) was created inside the `my_launch_pkg` package to start `turtlesim_node` and `turtle_teleop_key` together in a single command.
2. **Follow-the-leader launch** — A second launch file (`follow_the_leader_launch.py`) was created that additionally spawns a second turtle (`turtle2`) and starts a custom `follower_node` that implements a proportional (P) controller so turtle2 follows turtle1 in real time.
3. **Rosbag recording** — While driving turtle1 with keyboard teleop, the `/turtle1/cmd_vel` topic was recorded using `ros2 bag record`.
4. **rqt_plot visualization** — The recorded and live `/turtle1/cmd_vel` data were visualized in `rqt_plot` to observe the velocity commands over time.
5. **Trajectory extraction** — A Python script (`extract_trajectory.py`) was written to read the rosbag's SQLite3 database directly, deserialize the CDR-encoded Twist messages, and export them to a CSV file (`trajectory_data.csv`).

---

## 2. Observations

1. **Launch files** simplify the startup of multi-node systems significantly — spawning `turtlesim_node`, `teleop`, `turtle2`, and the custom `follower_node` all in one `ros2 launch` command.
2. **Rosbag** is effective for offline analysis. Even without replaying visually, the raw data can be extracted, parsed, and analysed from the SQLite3 database.
3. **rqt_plot** clearly shows the step-function nature of keyboard teleop commands: the velocities jump between 0 and ±2.0 with no intermediate values.
4. **Follow-the-leader** behaviour was implemented using a simple P-controller with gains of 1.5 (linear) and 6.0 (angular). The follower stops within 0.5 units of the leader to avoid collision.

---

## 3. Files Produced

| File | Description |
|---|---|
| `turtlesim_launch.py` | Basic launch: turtlesim + teleop |
| `follow_the_leader_launch.py` | Launch: turtlesim + turtle2 + follower + teleop |
| `follower_node.py` | P-controller node for follow-the-leader |
| `extract_trajectory.py` | Script to extract rosbag data to CSV |
| `trajectory_data.csv` | 128 rows × 7 columns of extracted cmd_vel data |
| `rosbag_analysis.txt` | Detailed analysis of the extracted trajectory data |
| `cmd_vel_graph.png` / `cmd_vel_graphs.png` | rqt_plot screenshots of velocity commands |
| `launch_process.png` | Screenshot of the launch process |
| `week4_rqt_graph.png` | rqt_graph screenshot showing node/topic connections |
