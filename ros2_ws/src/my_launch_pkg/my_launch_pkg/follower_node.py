import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
import math

class FollowerNode(Node):
    def __init__(self):
        super().__init__('follower_node')
        
        # Subscriptions to get positions
        self.leader_pose = None
        self.follower_pose = None
        
        self.create_subscription(Pose, '/turtle1/pose', self.leader_callback, 10)
        self.create_subscription(Pose, '/turtle2/pose', self.follower_callback, 10)
        
        # Publisher to move turtle2
        self.publisher = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)
        
        # Timer to run the control loop at 10Hz
        self.timer = self.create_timer(0.1, self.control_loop)
        
        self.get_logger().info('Follower node has been started!')

    def leader_callback(self, msg):
        self.leader_pose = msg

    def follower_callback(self, msg):
        self.follower_pose = msg

    def control_loop(self):
        if self.leader_pose is None or self.follower_pose is None:
            return

        # Calculate distance (Linear Error)
        dx = self.leader_pose.x - self.follower_pose.x
        dy = self.leader_pose.y - self.follower_pose.y
        distance = math.sqrt(dx**2 + dy**2)

        # Calculate angle to target (Angular Error)
        angle_to_target = math.atan2(dy, dx)
        angle_error = angle_to_target - self.follower_pose.theta
        
        # Normalize angle error to [-pi, pi]
        if angle_error > math.pi:
            angle_error -= 2 * math.pi
        elif angle_error < -math.pi:
            angle_error += 2 * math.pi

        msg = Twist()
        
        # Simple P-Controller
        if distance > 0.5:  # Don't crash into the leader
            msg.linear.x = 1.5 * distance
            msg.angular.z = 6.0 * angle_error
        else:
            msg.linear.x = 0.0
            msg.angular.z = 0.0

        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = FollowerNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
