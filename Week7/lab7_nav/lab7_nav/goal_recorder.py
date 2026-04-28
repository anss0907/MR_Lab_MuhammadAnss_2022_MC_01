#!/usr/bin/env python3
"""
Goal Recorder Node — records Nav2 navigation goals to a CSV file.

Subscribes to /plan (nav_msgs/msg/Path) published by the Nav2 planner.
The last pose in the planned path IS the navigation goal.
Includes deduplication so replanning to the same goal doesn't create duplicates.

Usage:
    ros2 run lab7_nav goal_recorder
"""

import os
import csv
import math
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from nav_msgs.msg import Path


# Absolute path — always saves to the source package directory
CSV_PATH = '/home/anss0907/MR_Lab_MuhammadAnss/ros2_ws/src/lab7_nav/RecordedGoalPoints/RecordedGoalPoints.csv'

# Minimum distance (m) between goals to count as a NEW waypoint
# This prevents duplicate entries when Nav2 replans to the same goal
DEDUP_THRESHOLD = 0.3


class GoalRecorder(Node):

    def __init__(self):
        super().__init__('goal_recorder')

        # Ensure output directory exists
        os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
        self.csv_path = CSV_PATH
        self.goal_count = 0
        self.last_goal = None  # (x, y) of last recorded goal for dedup

        # Write CSV header if file is missing or empty
        write_header = (not os.path.exists(self.csv_path)
                        or os.path.getsize(self.csv_path) == 0)
        if write_header:
            with open(self.csv_path, 'w', newline='') as f:
                csv.writer(f).writerow([
                    'waypoint_id',
                    'pos_x', 'pos_y', 'pos_z',
                    'orient_x', 'orient_y', 'orient_z', 'orient_w',
                    'frame_id'
                ])
            self.get_logger().info(f'Created CSV: {self.csv_path}')
        else:
            # Resume counting from existing rows
            with open(self.csv_path, 'r') as f:
                rows = list(csv.reader(f))
                self.goal_count = max(0, len(rows) - 1)
                if len(rows) > 1:
                    last = rows[-1]
                    self.last_goal = (float(last[1]), float(last[2]))
            self.get_logger().info(
                f'Resuming — {self.goal_count} goals already recorded.')

        # Subscribe to /plan — Nav2 planner publishes the global path here
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            depth=10
        )
        self.create_subscription(Path, '/plan', self.plan_cb, qos)

        self.get_logger().info('='*50)
        self.get_logger().info('Goal Recorder is RUNNING')
        self.get_logger().info('Listening on: /plan')
        self.get_logger().info(f'Saving to:    {self.csv_path}')
        self.get_logger().info('Send Nav2 Goals in RViz — they will be recorded!')
        self.get_logger().info('='*50)

    def plan_cb(self, msg: Path):
        """Called when Nav2 planner publishes a new global path."""
        if not msg.poses:
            return

        # The LAST pose in the path is the navigation goal
        goal_pose = msg.poses[-1]
        p = goal_pose.pose.position
        o = goal_pose.pose.orientation
        frame = goal_pose.header.frame_id or msg.header.frame_id

        # Deduplication — skip if goal is very close to the last recorded one
        if self.last_goal is not None:
            dist = math.sqrt((p.x - self.last_goal[0])**2 +
                             (p.y - self.last_goal[1])**2)
            if dist < DEDUP_THRESHOLD:
                return  # same goal, Nav2 is just replanning

        # Record this new goal
        self.goal_count += 1
        self.last_goal = (p.x, p.y)

        with open(self.csv_path, 'a', newline='') as f:
            csv.writer(f).writerow([
                self.goal_count,
                f'{p.x:.4f}', f'{p.y:.4f}', f'{p.z:.4f}',
                f'{o.x:.4f}', f'{o.y:.4f}', f'{o.z:.4f}', f'{o.w:.4f}',
                frame
            ])

        self.get_logger().info(
            f'*** RECORDED WP {self.goal_count}: '
            f'x={p.x:.3f}  y={p.y:.3f}  '
            f'oz={o.z:.3f}  ow={o.w:.3f}  '
            f'frame={frame} ***')


def main(args=None):
    rclpy.init(args=args)
    node = GoalRecorder()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info(f'Shutting down. {node.goal_count} goals recorded total.')
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
