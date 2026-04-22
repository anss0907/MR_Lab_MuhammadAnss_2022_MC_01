"""
LiDAR-based Reactive Navigation Node for TurtleBot3
Lab Manual 6 - MCT-454L Mobile Robotics

Implements 5 tasks:
  Task 1: Scan Processing     (mode: scan_only)
  Task 2: Stop-on-Obstacle    (mode: stop)
  Task 3: Obstacle Avoidance  (mode: avoid)
  Task 4: Wall Following      (mode: wall_follow)
  Task 5: Behavior Sequencing (mode: full)   <-- default

Usage:
  ros2 run lidar_nav_lab6 lidar_navigator
  ros2 run lidar_nav_lab6 lidar_navigator --ros-args -p mode:=stop
"""

import rclpy
import numpy as np
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


class LidarNavigator(Node):
    """Reactive navigator using LaserScan data."""

    # ── Tunables ────────────────────────────────────────────────
    FRONT_THRESHOLD = 0.2        # metres – stop / react distance
    SIDE_THRESHOLD  = 0.2        # metres – wall-follow set-point
    LINEAR_SPEED    = 0.15       # m/s   – forward cruise speed
    ANGULAR_SPEED   = 0.5        # rad/s – turning speed
    WALL_KP         = 1.5        # proportional gain for wall-follow
    # ────────────────────────────────────────────────────────────

    VALID_MODES = ('scan_only', 'stop', 'avoid', 'wall_follow', 'full')

    def __init__(self):
        super().__init__('lidar_navigator')

        # Declare and read the 'mode' parameter (default = full)
        self.declare_parameter('mode', 'full')
        self.mode = self.get_parameter('mode').get_parameter_value().string_value
        if self.mode not in self.VALID_MODES:
            self.get_logger().warn(
                f"Unknown mode '{self.mode}', falling back to 'full'")
            self.mode = 'full'
        self.get_logger().info(f'=== LidarNavigator started in [{self.mode}] mode ===')

        # Publishers / Subscribers
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.scan_sub = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)

    # ================================================================
    #  TASK 1 — Scan Processing
    # ================================================================
    def _process_scan(self, msg):
        """Clean data, split into regions, return min distances using numpy."""
        ranges = np.array(msg.ranges)
        n = len(ranges)

        # Replace inf / NaN or values outside range with max_range
        valid_mask = np.isfinite(ranges) & (ranges > msg.range_min) & (ranges < msg.range_max)
        clean = np.where(valid_mask, ranges, msg.range_max)

        # Divide into regions using indices
        # 0 is front, increases CCW. 
        # Front: 330° to 30°
        front_idx = np.concatenate([np.arange(int(330/360*n), n), np.arange(0, int(30/360*n))])
        left_idx  = np.arange(int(60/360*n), int(120/360*n))
        right_idx = np.arange(int(240/360*n), int(300/360*n))

        front_dist = np.min(clean[front_idx])
        left_dist  = np.min(clean[left_idx])
        right_dist = np.min(clean[right_idx])

        return front_dist, left_dist, right_dist

    # ================================================================
    #  Callback — dispatches to the active behaviour mode
    # ================================================================
    def scan_callback(self, msg):
        front, left, right = self._process_scan(msg)

        # Always log distances
        self.get_logger().info(
            f'Front: {front:.2f} m | Left: {left:.2f} m | Right: {right:.2f} m')

        twist = Twist()

        if self.mode == 'scan_only':
            # Task 1 — just print, no motion
            pass

        elif self.mode == 'stop':
            # Task 2 — move forward, stop at obstacle
            twist = self._stop_on_obstacle(front)

        elif self.mode == 'avoid':
            # Task 3 — obstacle avoidance
            twist = self._obstacle_avoidance(front, left, right)

        elif self.mode == 'wall_follow':
            # Task 4 — wall following (right wall)
            twist = self._wall_follow(front, right)

        elif self.mode == 'full':
            # Task 5 — behaviour sequencing
            twist = self._behaviour_sequencing(front, left, right)

        self.cmd_pub.publish(twist)

    # ================================================================
    #  TASK 2 — Stop-on-Obstacle
    # ================================================================
    def _stop_on_obstacle(self, front_dist):
        twist = Twist()
        if front_dist < self.FRONT_THRESHOLD:
            self.get_logger().warn('OBSTACLE detected — stopping!')
            twist.linear.x = 0.0
            twist.angular.z = 0.0
        else:
            twist.linear.x = self.LINEAR_SPEED
            twist.angular.z = 0.0
        return twist

    # ================================================================
    #  TASK 3 — Obstacle Avoidance
    # ================================================================
    def _obstacle_avoidance(self, front, left, right):
        twist = Twist()
        if front < self.FRONT_THRESHOLD:
            twist.linear.x = 0.0
            if left >= right:
                twist.angular.z = self.ANGULAR_SPEED   # turn left (CCW)
                self.get_logger().info('Avoiding → turning LEFT')
            else:
                twist.angular.z = -self.ANGULAR_SPEED  # turn right (CW)
                self.get_logger().info('Avoiding → turning RIGHT')
        else:
            twist.linear.x = self.LINEAR_SPEED
            twist.angular.z = 0.0
        return twist

    # ================================================================
    #  TASK 4 — Wall Following (right wall, proportional control)
    # ================================================================
    def _wall_follow(self, front, right):
        twist = Twist()
        if front < self.FRONT_THRESHOLD:
            twist.linear.x = 0.0
            twist.angular.z = self.ANGULAR_SPEED
            self.get_logger().info('Wall-follow: front blocked, turning left')
        else:
            error = self.SIDE_THRESHOLD - right
            twist.linear.x = self.LINEAR_SPEED
            twist.angular.z = self.WALL_KP * error
            twist.angular.z = max(-self.ANGULAR_SPEED,
                                  min(self.ANGULAR_SPEED, twist.angular.z))
            self.get_logger().info(
                f'Wall-follow: right={right:.2f} err={error:.2f} '
                f'ang_z={twist.angular.z:.2f}')
        return twist

    # ================================================================
    #  TASK 5 — Behaviour Sequencing
    # ================================================================
    def _behaviour_sequencing(self, front, left, right):
        """
        Priority-based reactive controller:
          1. If obstacle ahead → avoid (turn toward larger gap)
          2. If a wall is close on the right → wall-follow
          3. Otherwise → cruise forward
        """
        if front < self.FRONT_THRESHOLD:
            self.get_logger().info('[SEQ] Obstacle ahead — calling Avoidance')
            return self._obstacle_avoidance(front, left, right)

        elif right < self.SIDE_THRESHOLD * 1.5:
            self.get_logger().info('[SEQ] Wall nearby — calling Wall Following')
            return self._wall_follow(front, right)

        else:
            self.get_logger().info('[SEQ] Path clear — cruising forward')
            twist = Twist()
            twist.linear.x = self.LINEAR_SPEED
            twist.angular.z = 0.0
            return twist


def main(args=None):
    rclpy.init(args=args)
    node = LidarNavigator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down LidarNavigator...')
    finally:
        stop_msg = Twist()
        node.cmd_pub.publish(stop_msg)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
