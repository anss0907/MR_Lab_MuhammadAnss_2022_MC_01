#!/usr/bin/env python3
"""
Task 2: Multi-Waypoint Navigation using first 5 recorded goal points.
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import FollowWaypoints
from geometry_msgs.msg import PoseStamped


class WaypointNavigatorTask2(Node):
    def __init__(self):
        super().__init__('waypoint_navigator_task2')
        self._client = ActionClient(self, FollowWaypoints, 'follow_waypoints')

    def make_pose(self, x, y, oz, ow):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = 0.0
        pose.pose.orientation.x = 0.0
        pose.pose.orientation.y = 0.0
        pose.pose.orientation.z = oz
        pose.pose.orientation.w = ow
        return pose

    def send_waypoints(self, waypoints):
        self.get_logger().info('Waiting for FollowWaypoints action server...')
        self._client.wait_for_server()

        goal_msg = FollowWaypoints.Goal()
        goal_msg.poses = waypoints

        self.get_logger().info('='*50)
        self.get_logger().info(f'Sending {len(waypoints)} waypoints to Nav2...')
        for i, wp in enumerate(waypoints, 1):
            self.get_logger().info(
                f'  WP {i}: x={wp.pose.position.x:.4f}  '
                f'y={wp.pose.position.y:.4f}  '
                f'oz={wp.pose.orientation.z:.4f}  '
                f'ow={wp.pose.orientation.w:.4f}')
        self.get_logger().info('='*50)

        send_goal_future = self._client.send_goal_async(
            goal_msg, feedback_callback=self.feedback_cb)
        rclpy.spin_until_future_complete(self, send_goal_future)

        goal_handle = send_goal_future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected by server!')
            return

        self.get_logger().info('Goal accepted! Robot is navigating...')
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        result = result_future.result().result
        missed = result.missed_waypoints
        if missed:
            self.get_logger().warn(f'Missed waypoints: {list(missed)}')
        else:
            self.get_logger().info('All waypoints reached successfully!')

    def feedback_cb(self, feedback_msg):
        current_wp = feedback_msg.feedback.current_waypoint
        self.get_logger().info(
            f'>> Currently heading to waypoint {current_wp + 1}')


def main(args=None):
    rclpy.init(args=args)
    navigator = WaypointNavigatorTask2()

    # First 5 recorded goal points from RecordedGoalPoints.csv
    waypoints = [
        navigator.make_pose(1.4513,  0.9929, -0.0075, 1.0000),   # WP 1
        navigator.make_pose(2.5944,  1.0477, -0.7189, 0.6952),   # WP 2
        navigator.make_pose(2.4980, -0.0532, -0.0075, 1.0000),   # WP 3
        navigator.make_pose(3.7521, -0.0561,  0.6965, 0.7176),   # WP 4
        navigator.make_pose(3.7535,  1.1022,  0.7777, 0.6287),   # WP 5
    ]

    navigator.get_logger().info(f'Loaded {len(waypoints)} waypoints. Starting navigation...')
    navigator.send_waypoints(waypoints)

    navigator.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
