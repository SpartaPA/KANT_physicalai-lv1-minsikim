import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist

from std_srvs.srv import SetBool, Trigger
from turtlesim.msg import Pose

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
        
        self.is_running = True
        self.home_x = 0.0
        self.home_y = 0.0

        self.drive_service = self.create_service(
            SetBool,
            '/turtle1/set_driving',
            self.set_driving_callback
        )

        self.home_service = self.create_service(
            Trigger,
            '/turtle1/save_home',
            self.save_home_callback
        )
        
        self.current_x = 0.0
        self.current_y = 0.0

        self.pose_subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )
                
    def control(self):
        msg = Twist()

        if not self.is_running:
            self.publisher.publish(msg)
            return
        
        elapsed = (
            self.get_clock().now() - self.start_time
        ).nanoseconds / 1e9
        

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
            return

        self.publisher.publish(msg)
    
    def set_driving_callback(self, request, response):
        if request.data:
            # 정지 상태에서 다시 시작
            if not self.is_running:
                paused_time = (
                    self.get_clock().now() - self.pause_start_time
                )
                self.start_time += paused_time

            self.is_running = True
            response.success = True
            response.message = 'Driving enabled'

        else:
            # 주행 중 → 정지
            if self.is_running:
                self.pause_start_time = self.get_clock().now()

            self.is_running = False
            response.success = True
            response.message = 'Driving disabled'

        return response
    
    def pose_callback(self, msg):
        self.current_x = msg.x
        self.current_y = msg.y
    
    def save_home_callback(self, request, response):
        self.home_x = self.current_x
        self.home_y = self.current_y

        response.success = True
        response.message = (
            f'Home saved: ({self.home_x:.2f}, {self.home_y:.2f})'
        )

        return response
        
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