#!/usr/bin/env python3
import math

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Twist
from nav2_msgs.action import FollowPath
from nav_msgs.msg import Odometry, Path


def yaw_to_quaternion(yaw):
    return [0.0, 0.0, math.sin(yaw / 2.0), math.cos(yaw / 2.0)]


class CircleDriverNode(Node):
    def __init__(self):
        super().__init__('circle_driver_node')
        self.declare_parameter('linear_speed', 0.3)
        self.declare_parameter('circle_radius', 2.0)
        self.declare_parameter('num_waypoints', 60)
        self.declare_parameter('send_rate', 5.0)

        self.linear_speed = self.get_parameter('linear_speed').value
        self.circle_radius = self.get_parameter('circle_radius').value
        self.num_waypoints = self.get_parameter('num_waypoints').value
        send_rate = self.get_parameter('send_rate').value

        self.current_odom = None
        self.goal_in_progress = False

        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10
        )

        self.action_client = ActionClient(
            self, FollowPath, 'follow_path'
        )

        self.timer = self.create_timer(1.0 / send_rate, self.timer_callback)

        self.get_logger().info(
            f'Circle driver started: radius={self.circle_radius} m, '
            f'speed={self.linear_speed} m/s, waypoints={self.num_waypoints}'
        )

    def odom_callback(self, msg):
        self.current_odom = msg

    def generate_circle_path(self):
        odom = self.current_odom
        x = odom.pose.pose.position.x
        y = odom.pose.pose.position.y
        q = odom.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        center_x = x + self.circle_radius * math.cos(yaw + math.pi / 2.0)
        center_y = y + self.circle_radius * math.sin(yaw + math.pi / 2.0)

        start_angle = math.atan2(y - center_y, x - center_x)

        path = Path()
        path.header.frame_id = 'odom'
        path.header.stamp = self.get_clock().now().to_msg()

        # Generate 90% of the circle to prevent instant goal completion
        target_waypoints = int(self.num_waypoints * 0.9)

        for i in range(target_waypoints):
            angle = start_angle + 2.0 * math.pi * i / self.num_waypoints
            px = center_x + self.circle_radius * math.cos(angle)
            py = center_y + self.circle_radius * math.sin(angle)

            tangent = angle + math.pi / 2.0

            pose = PoseStamped()
            pose.header.frame_id = 'odom'
            pose.header.stamp = self.get_clock().now().to_msg()
            pose.pose.position.x = px
            pose.pose.position.y = py
            pose.pose.position.z = 0.0
            quat = yaw_to_quaternion(tangent)
            pose.pose.orientation.x = quat[0]
            pose.pose.orientation.y = quat[1]
            pose.pose.orientation.z = quat[2]
            pose.pose.orientation.w = quat[3]
            path.poses.append(pose)

        return path

    def timer_callback(self):
        if self.current_odom is None:
            return
        if self.goal_in_progress:
            return

        path = self.generate_circle_path()

        if not self.action_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().warn('Controller server not ready', throttle_duration_sec=5.0)
            return

        goal = FollowPath.Goal()
        goal.path = path
        goal.controller_id = 'FollowPath'

        self.goal_in_progress = True
        send_goal_future = self.action_client.send_goal_async(
            goal, feedback_callback=self.feedback_callback
        )
        send_goal_future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback_msg):
        pass

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn('FollowPath goal rejected')
            self.goal_in_progress = False
            return

        self.get_logger().info('FollowPath goal accepted, tracking circle')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        result = future.result()
        status = result.status

        if status == 4:
            self.get_logger().info('Circle path completed successfully, sending next loop')
        elif status == 5:
            self.get_logger().info('Circle path canceled, will resend')
        elif status == 6:
            self.get_logger().warn('Circle path aborted, will retry')

        self.goal_in_progress = False


def main(args=None):
    rclpy.init(args=args)
    node = CircleDriverNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        # Add the if check here to prevent the crash on exit
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
