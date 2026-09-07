import rclpy
from rclpy.node import Node

from turtlesim.srv import TeleportAbsolute
from turtlesim.srv import SetPen
from turtlesim.srv import Spawn
from std_srvs.srv import Empty


class ServiceClient(Node):

    def __init__(self):
        super().__init__('service_client')

        self.teleport_client = self.create_client(
            TeleportAbsolute,
            '/turtle1/teleport_absolute'
        )

        self.pen_client = self.create_client(
            SetPen,
            '/turtle1/set_pen'
        )

        self.spawn_client = self.create_client(
            Spawn,
            '/spawn'
        )

        self.clear_client = self.create_client(
            Empty,
            '/clear'
        )

    def call_service(self, client, request):
        future = client.call_async(request)

        rclpy.spin_until_future_complete(
            self,
            future
        )

        return future.result()

    def run(self):

        # 1. 순간이동
        teleport_request = TeleportAbsolute.Request()
        teleport_request.x = 2.0
        teleport_request.y = 2.0
        teleport_request.theta = 0.0

        result = self.call_service(
            self.teleport_client,
            teleport_request
        )

        self.get_logger().info(
            'teleport_absolute 호출 완료'
        )

        # 2. 펜 설정
        pen_request = SetPen.Request()
        pen_request.r = 255
        pen_request.g = 0
        pen_request.b = 0
        pen_request.width = 3
        pen_request.off = False

        result = self.call_service(
            self.pen_client,
            pen_request
        )

        self.get_logger().info(
            'set_pen 호출 완료'
        )

        # 3. 거북이 추가
        spawn_request = Spawn.Request()
        spawn_request.x = 8.0
        spawn_request.y = 2.0
        spawn_request.theta = 0.0
        spawn_request.name = 'turtle2'

        result = self.call_service(
            self.spawn_client,
            spawn_request
        )

        self.get_logger().info(
            f'spawn 호출 완료: {result.name}'
        )

        # 4. 궤적 지우기
        clear_request = Empty.Request()

        result = self.call_service(
            self.clear_client,
            clear_request
        )

        self.get_logger().info(
            'clear 호출 완료'
        )


def main(args=None):
    rclpy.init(args=args)

    node = ServiceClient()

    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()