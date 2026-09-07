import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist

class SquareNode(Node):
    def __init__(self):
        super().__init__('square_node')
    
        self.publisher = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )
        
        self.state = 0
        self.start_time = self.get_clock().now()
        
        self.timer = self.create_timer(
            0.01,
            self.control
        )
        
    def control(self):
        elapsed = (
            self.get_clock().now() - self.start_time
        ).nanoseconds / 1e9
        
        msg = Twist()

        if self.state % 2 == 0:
            # 전진
            msg.linear.x = 1.0

            if elapsed >= 2.0:
                self.state += 1
                self.start_time = self.get_clock().now()

        else:
            # 제자리 회전
            msg.angular.z = math.pi / 2.0

            if elapsed >= 1.0:
                self.state += 1
                self.start_time = self.get_clock().now()

        if self.state >= 8: # 종료
            msg.linear.x = 0.0
            msg.angular.z = 0.0

            self.publisher.publish(msg)
            self.timer.cancel()
            return

        self.publisher.publish(msg)
        
def main(args=None):
    rclpy.init(args=args)

    node = SquareNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()