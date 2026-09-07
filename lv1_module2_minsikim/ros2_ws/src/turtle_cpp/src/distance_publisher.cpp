#include <chrono>
#include <cmath>
#include <functional>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float32.hpp"
#include "turtlesim/msg/pose.hpp"

class DistancePublisher : public rclcpp::Node
{
public:
    DistancePublisher() : Node("distance_publisher")
    {
        pose_subscription_ = this->create_subscription<turtlesim::msg::Pose>(
            "/turtle1/pose",
            10,
            [this](const turtlesim::msg::Pose::SharedPtr msg)
            {
                this->pose_callback(msg);
            }
        );

        distance_publisher_ =
            this->create_publisher<std_msgs::msg::Float32>(
                "/turtle_distance",
                10
            );

        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(100),
            [this]()
            {
                this->publish_distance();
            }
        );
    }

private:
    void pose_callback(
        const turtlesim::msg::Pose::SharedPtr msg)
    {
        latest_x_ = msg->x;
        latest_y_ = msg->y;
    }

    void publish_distance()
    {
        double distance =
            std::sqrt(
                latest_x_ * latest_x_ +
                latest_y_ * latest_y_
            );

        std_msgs::msg::Float32 msg;
        msg.data = static_cast<float>(distance);

        distance_publisher_->publish(msg);
    }

    double latest_x_ = 0.0;
    double latest_y_ = 0.0;

    rclcpp::Subscription<turtlesim::msg::Pose>::SharedPtr
        pose_subscription_;

    rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr
        distance_publisher_;

    rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);

    auto node = std::make_shared<DistancePublisher>();

    rclcpp::spin(node);

    rclcpp::shutdown();

    return 0;
}