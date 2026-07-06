#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class CmdVelListener(Node):
    def __init__(self):
        super().__init__('cmd_vel_listener')
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.listener_callback,
            10
        )
        self.subscription 
        self.get_logger().info("CMD Vel Listener Node has been started.")

    def listener_callback(self, msg):
        linear_x = msg.linear.x
        angular_z = msg.angular.z
        
        self.get_logger().info(f"Linear: {linear_x:.2f} m/s, Angular: {angular_z:.2f} rad/s")

def main(args=None):
    rclpy.init(args=args)
    node = CmdVelListener()
    rclpy.spin(node)
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
