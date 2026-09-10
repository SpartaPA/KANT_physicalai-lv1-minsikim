import math

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from turtlesim.action import RotateAbsolute


class RotateClient(Node):
    def __init__(self):
        super().__init__('rotate_client')

        self.action_client = ActionClient(
            self,
            RotateAbsolute,
            '/turtle1/rotate_absolute'
        )
        
        self.goal_handle = None

    def send_goal(self, theta):
        self.get_logger().info(
            f'회전 목표 전송: {theta:.2f} rad'
        )

        # Action Server가 준비될 때까지 기다림
        self.action_client.wait_for_server()

        # Goal 생성
        goal_msg = RotateAbsolute.Goal()
        goal_msg.theta = theta

        # 비동기로 Goal 전송
        future = self.action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        # Goal 응답이 오면 처리
        future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().info('Goal이 거부되었습니다.')
            rclpy.shutdown()
            return

        self.goal_handle = goal_handle

        self.get_logger().info('Goal이 승인되었습니다.')

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def feedback_callback(self, feedback_msg):
        remaining = feedback_msg.feedback.remaining

        self.get_logger().info(
            f'남은 회전량: {remaining:.3f} rad'
        )

    def result_callback(self, future):
        result = future.result().result

        self.get_logger().info(
            f'회전 완료 - 실제 회전량: {result.delta:.3f} rad'
        )

        rclpy.shutdown()
        
    def cancel_goal(self):
        if self.goal_handle is None:
            self.get_logger().info('취소할 Goal이 없습니다.')
            return

        self.get_logger().info('Goal 취소 요청')

        future = self.goal_handle.cancel_goal_async()
        future.add_done_callback(self.cancel_callback)

        # 타이머 제거
        self.cancel_timer.cancel()


    def cancel_callback(self, future):
        cancel_response = future.result()

        if len(cancel_response.goals_canceling) > 0:
            self.get_logger().info('Goal 취소 성공')
        else:
            self.get_logger().info('Goal 취소 실패')


def main(args=None):
    rclpy.init(args=args)

    node = RotateClient()

    # 예: 90도 = pi/2
    node.send_goal(math.pi/2)
    
    node.cancel_timer = node.create_timer(
        .5,
        node.cancel_goal
    )

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