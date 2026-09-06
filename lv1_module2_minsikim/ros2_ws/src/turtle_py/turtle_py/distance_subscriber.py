import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32

class DistanceSubscriber(Node):
    def __init__(self):
        super().__init__('distance_subscriber')
        
        self.declare_parameter('warn_distance', 2.5)
        
        self.distance_subscription = self.create_subscription(
            Float32,
            '/turtle_distance',
            self.distance_callback,
            10
        )
        
    def distance_callback(self, msg):
        warn_distance = self.get_parameter('warn_distance').value

        if msg.data > warn_distance:
            self.get_logger().warn(
                f'Distance warning: {msg.data:.3f} m'
            )
        
        
def main(args=None):
    rclpy.init(args=args)

    node = DistanceSubscriber()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()