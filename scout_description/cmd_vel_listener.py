import rclpy
import rclpy.node import Node

class CmdVelSubscriber(Node):
    def __init__(self):
        super().__init__("cmd_vel_subscriber")
    self.subscription = self.create_subscription(Twist,'/cmd_vel',self.listener_callback, 10)
    def listener_callback(self, msg:Twist):
        lin = msg.linear
        ang = msg.angular
        self.get_logger().info(msg)
    
def main(args=None):
    rclpy.init(args=args)
    node = CmdVelSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
