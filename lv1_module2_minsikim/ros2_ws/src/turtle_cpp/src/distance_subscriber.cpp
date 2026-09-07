#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float32.hpp"

class DistanceSubscriber : public rclcpp::Node
{
public:
    DistanceSubscriber()
    : Node("distance_subscriber")
    {
        subscription_ =
            this->create_subscription<std_msgs::msg::Float32>(
                "/turtle_distance",
                10,
                std::bind(
                    &DistanceSubscriber::distance_callback,
                    this,
                    std::placeholders::_1));
    }

private:
    void distance_callback(
        const std_msgs::msg::Float32::SharedPtr msg)
    {
        RCLCPP_INFO(
            this->get_logger(),
            "Distance: %.3f m",
            msg->data);
    }

    rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr
        subscription_;
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);

    auto node = std::make_shared<DistanceSubscriber>();

    rclcpp::spin(node);

    rclcpp::shutdown();

    return 0;
}