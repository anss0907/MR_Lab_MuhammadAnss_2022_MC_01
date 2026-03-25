import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.srv import Spawn
import time

class VelocityPublisher(Node):
    def __init__(self):
        super().__init__('velocity_publisher')

        # Service client for turtlesim spawn
        self.spawn_client = self.create_client(Spawn, '/spawn')

        # Publishers for 3 turtles
        self.pub1 = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pub2 = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)
        self.pub3 = self.create_publisher(Twist, '/turtle3/cmd_vel', 10)

        # Spawn 3 turtles at different locations
        self.setup_turtles()

        # simple shared timing
        self.linear_time = 2.0             # same for triangle + square
        self.common_turn_time = 1.0        # both rotate together
        self.extra_triangle_turn_time = 0.35  # triangle rotates more, square waits
        self.turn_speed = 1.5708           # ~90 deg/s

        self.total_cycle = self.linear_time + self.common_turn_time + self.extra_triangle_turn_time
        self.timer = self.create_timer(self.total_cycle, self.timer_callback)

        # start immediately once
        self.timer_callback()

    def setup_turtles(self):
        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /spawn service...')

        # Keep default turtle1 as-is; spawn only turtle2 and turtle3
        self.spawn_turtle(1.0, 2.0, 0.0, 'turtle2')
        self.spawn_turtle(3.0, 3.0, 0.0, 'turtle3')
    def spawn_turtle(self, x, y, theta, name):
        req = Spawn.Request()
        req.x = x
        req.y = y
        req.theta = theta
        req.name = name
        future = self.spawn_client.call_async(req)
        rclpy.spin_until_future_complete(self, future)

    def publish_for(
        self,
        duration_sec,
        c_lin, c_ang,
        tri_lin, tri_ang,
        sq_lin, sq_ang,
        rate_hz=10
    ):
        msg1 = Twist()
        msg2 = Twist()
        msg3 = Twist()
        end_time = time.time() + duration_sec
        dt = 1.0 / rate_hz

        while time.time() < end_time:
            msg1.linear.x, msg1.angular.z = c_lin, c_ang
            self.pub1.publish(msg1)

            msg2.linear.x, msg2.angular.z = tri_lin, tri_ang
            self.pub2.publish(msg2)

            msg3.linear.x, msg3.angular.z = sq_lin, sq_ang
            self.pub3.publish(msg3)

            time.sleep(dt)

    def timer_callback(self):
        # Phase 1: both linear (same length/time), circle always same
        self.publish_for(
            self.linear_time,
            2.0, 1.0,
            1.5, 0.0,
            1.5, 0.0,
            rate_hz=10
        )

        # Phase 2: both rotate together
        self.publish_for(
            self.common_turn_time,
            2.0, 1.0,
            0.0, self.turn_speed,
            0.0, self.turn_speed,
            rate_hz=10
        )

        # Phase 3: triangle extra rotate, square waits
        self.publish_for(
            self.extra_triangle_turn_time,
            2.0, 1.0,
            0.0, self.turn_speed,
            0.0, 0.0,
            rate_hz=10
        )

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