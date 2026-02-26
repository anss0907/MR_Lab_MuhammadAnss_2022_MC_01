import os
import rclpy
from rclpy.node import Node


class Task2Node(Node):
    def __init__(self):
        super().__init__('w1_task2_node')

        counter_dir = os.path.join(os.path.expanduser('~'), 'ros2_ws', 'data')
        os.makedirs(counter_dir, exist_ok=True)
        counter_file = os.path.join(counter_dir, 'mr_lab_w1_task2_run_count.txt')

        try:
            with open(counter_file, 'r') as f:
                count = int(f.read().strip())
        except (FileNotFoundError, ValueError):
            count = 0

        count += 1

        with open(counter_file, 'w') as f:
            f.write(str(count))

        self.get_logger().info(f'Run count: {count}')


def main(args=None):
    rclpy.init(args=args)
    node = Task2Node()

    rclpy.spin_once(node, timeout_sec=0.1)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
