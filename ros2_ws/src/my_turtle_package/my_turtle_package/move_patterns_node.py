import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

class VelocityPublisher(Node):
    def __init__(self):
        super().__init__('velocity_publisher')
        self.publisher_ = self.create_publisher(Twist, 'turtle1/cmd_vel',10)
        timer_period = 0.5 # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
    def timer_callback(self):
        msg = Twist()

        def publish_for(duration_sec, linear_x, angular_z, rate_hz=10):
            msg.linear.x = linear_x
            msg.angular.z = angular_z
            end_time = time.time() + duration_sec
            dt = 1.0 / rate_hz
            while time.time() < end_time:
                self.publisher_.publish(msg)
                time.sleep(dt)

        # Circular pattern (continuous commands)
        publish_for(7, 2.0, 1.0)

        # Brief stop before next pattern
        publish_for(0.5, 0.0, 0.0)

        # Triangular pattern (3 sides, 120-degree turns)
        for _ in range(3):
            publish_for(2.0, 1.0, 0.0)      # side
            publish_for(1.0, 0.0, 2.094)    # turn ~120 deg

        # Final stop
        publish_for(0.2, 0.0, 0.0)
def main(args=None):
    rclpy.init(args=args)
    velocity_publisher = VelocityPublisher()
    rclpy.spin(velocity_publisher)
    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically # when the garbage collector destroys the node object)
    velocity_publisher.destroy_node()
    rclpy.shutdown()
if __name__ == '__main__': 
    main()