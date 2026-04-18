#!/usr/bin/env python3
"""
Lab Manual 5 - Task 8:
Publisher node that alternates between publishing forward velocity
and zero velocity every 2 seconds to the /cmd_vel topic.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class CmdVelPublisher(Node):
    def __init__(self):
        super().__init__('cmd_vel_publisher')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(2.0, self.timer_callback)
        self.moving = False  # Toggle flag
        self.get_logger().info('CmdVel Publisher started — alternating every 2 seconds')

    def timer_callback(self):
        msg = Twist()
        if self.moving:
            # Zero velocity (stop)
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.get_logger().info('Publishing: STOP (linear.x=0.0)')
        else:
            # Forward velocity
            msg.linear.x = 0.2
            msg.angular.z = 0.0
            self.get_logger().info('Publishing: FORWARD (linear.x=0.2)')

        self.publisher_.publish(msg)
        self.moving = not self.moving  # Toggle for next callback


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Stop the robot before shutting down
        stop_msg = Twist()
        node.publisher_.publish(stop_msg)
        node.get_logger().info('Stopping robot and shutting down.')
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
