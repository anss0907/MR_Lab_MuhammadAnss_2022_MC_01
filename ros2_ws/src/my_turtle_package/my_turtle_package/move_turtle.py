import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist 
from std_msgs.msg import String 
import time

class VelocityPublisher(Node):
    def __init__(self):
        super().__init__('velocity_publisher')
        self.publisher_ = self.create_publisher(Twist, 'turtle1/cmd_vel',10)
        timer_period = 0.5 # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
    def timer_callback(self):
        msg = Twist()
        for _ in range(4): 
            # Move in a square 
            msg.linear.x = 2.0 # Move forward 
            msg.angular.z = 0.0 
            self.publisher_.publish(msg)
        time.sleep(2)
        msg.linear.x = 0.0
        msg.angular.z = 1.57 # Turn 90 degrees
        self.publisher_.publish(msg) 
        time.sleep(1)
        #msg.linear.x = 0.0
        #msg.angular.z = 0.0 #self.publisher_.publish(msg)
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