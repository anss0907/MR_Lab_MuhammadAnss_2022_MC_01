import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose


class VelocityPublisher(Node):
    def __init__(self):
        super().__init__('go_to_goal_controller')

        # Topic-only interfaces
        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose_sub = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.goal_sub = self.create_subscription(Pose, '/turtle1/goal_pose', self.goal_callback, 10)

        # State
        self.current_pose = None
        self.goal_pose = None

        # Controller params
        self.k_linear = 1.5
        self.k_angular = 6.0
        self.max_linear = 2.0
        self.max_angular = 4.0
        self.pos_tolerance = 0.05
        self.heading_tolerance = 0.1

        # Control loop
        self.timer = self.create_timer(0.1, self.control_loop)
        self.get_logger().info('Go-to-goal controller started. Publish goal on /turtle1/goal_pose')

    def pose_callback(self, msg: Pose):
        self.current_pose = msg

    def goal_callback(self, msg: Pose):
        self.goal_pose = msg
        self.get_logger().info(f'New goal: x={msg.x:.2f}, y={msg.y:.2f}')

    def normalize_angle(self, angle: float) -> float:
        return math.atan2(math.sin(angle), math.cos(angle))

    def control_loop(self):
        if self.current_pose is None or self.goal_pose is None:
            return

        dx = self.goal_pose.x - self.current_pose.x
        dy = self.goal_pose.y - self.current_pose.y
        distance = math.sqrt(dx * dx + dy * dy)

        cmd = Twist()

        if distance < self.pos_tolerance:
            self.cmd_pub.publish(cmd)  # stop
            return

        target_heading = math.atan2(dy, dx)
        heading_error = self.normalize_angle(target_heading - self.current_pose.theta)

        # Rotate first if heading error is large, else move + steer
        if abs(heading_error) > self.heading_tolerance:
            cmd.linear.x = 0.0
            cmd.angular.z = max(-self.max_angular, min(self.max_angular, self.k_angular * heading_error))
        else:
            cmd.linear.x = min(self.max_linear, self.k_linear * distance)
            cmd.angular.z = max(-self.max_angular, min(self.max_angular, self.k_angular * heading_error))

        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    velocity_publisher = VelocityPublisher()
    rclpy.spin(velocity_publisher)
    velocity_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()