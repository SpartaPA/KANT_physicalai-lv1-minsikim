import math

import rclpy
from rclpy.node import Node

from turtlesim.msg import Pose
from std_msgs.msg import Float32

class DistancePublisher(Node):
    def __init__(self):
        super().__init__('distance_publisher')
        
        self.latest_x = 0.0
        self.latest_y = 0.0
        
        self.pose_subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )
        self.distance_publisher = self.create_publisher(
            Float32,
            '/turtle_distance',
            10
        )
        
        self.declare_parameter('publish_rate', 10.0)
        publish_rate = self.get_parameter('publish_rate').value
        period = 1.0 / publish_rate
        self.timer = self.create_timer(
            period,
            self.publish_distance
        )
        
    def pose_callback(self, msg):
        self.latest_x = msg.x
        self.latest_y = msg.y
        
    def publish_distance(self):
        distance = math.sqrt(self.latest_x ** 2 + self.latest_y ** 2)
        msg = Float32()
        msg.data = float(distance)
        
        self.distance_publisher.publish(msg)
        
        
def main(args=None):
    rclpy.init(args=args)

    node = DistancePublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()