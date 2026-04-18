#!/usr/bin/env python3
"""
Lab Manual 5 - Task 9:
Subscriber node that subscribes to /odom topic and prints received messages.
Message type: nav_msgs/msg/Odometry
"""

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry


class OdomSubscriber(Node):
    def __init__(self):
        super().__init__('odom_subscriber')
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )
        self.get_logger().info('Odom Subscriber started — listening on /odom')
        self.get_logger().info('Message type: nav_msgs/msg/Odometry')

    def odom_callback(self, msg):
        # Extract position
        pos = msg.pose.pose.position
        # Extract orientation (quaternion)
        orient = msg.pose.pose.orientation
        # Extract linear and angular velocity
        lin_vel = msg.twist.twist.linear
        ang_vel = msg.twist.twist.angular

        self.get_logger().info(
            f'Position    -> x: {pos.x:.4f}, y: {pos.y:.4f}, z: {pos.z:.4f}'
        )
        self.get_logger().info(
            f'Orientation -> x: {orient.x:.4f}, y: {orient.y:.4f}, '
            f'z: {orient.z:.4f}, w: {orient.w:.4f}'
        )
        self.get_logger().info(
            f'Linear Vel  -> x: {lin_vel.x:.4f}, y: {lin_vel.y:.4f}, z: {lin_vel.z:.4f}'
        )
        self.get_logger().info(
            f'Angular Vel -> x: {ang_vel.x:.4f}, y: {ang_vel.y:.4f}, z: {ang_vel.z:.4f}'
        )
        self.get_logger().info('---')


def main(args=None):
    rclpy.init(args=args)
    node = OdomSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
