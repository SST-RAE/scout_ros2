#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class CircleDriverNode(Node):
    def __init__(self):
        super().__init__('circle_driver_node')
        self.declare_parameter('linear_speed', 0.3)
        self.declare_parameter('angular_speed', 0.5)
        self.declare_parameter('publish_rate', 20.0)

        self.linear_speed = self.get_parameter('linear_speed').value
        self.angular_speed = self.get_parameter('angular_speed').value
        publish_rate = self.get_parameter('publish_rate').value

        self.publisher = self.create_publisher(Twist, 'cmd_vel_smoothed', 10)
        self.timer = self.create_timer(1.0 / publish_rate, self.timer_callback)

        self.get_logger().info(
            f'Circle driver started: linear={self.linear_speed} m/s, '
            f'angular={self.angular_speed} rad/s'
        )

    def timer_callback(self):
        msg = Twist()
        msg.linear.x = self.linear_speed
        msg.angular.z = self.angular_speed
        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = CircleDriverNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        stop_msg = Twist()
        node.publisher.publish(stop_msg)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
