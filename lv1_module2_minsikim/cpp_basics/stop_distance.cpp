#include <iostream>

int main() {
    double v, friction; // 속도(m/s), 마찰계수
    std::cin >> v >> friction;

    double g = 9.81;
    double a = friction * g;

    double distance = (v * v) / (2 * a);

    std::cout << "제동거리: " << distance << " m\n";

    return 0;
}