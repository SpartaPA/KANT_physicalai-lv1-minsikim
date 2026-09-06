#include <iostream>
#include "motor.hpp"

int main()
{
    Motor motor;

    motor.SetSpeed(10);

    std::cout << "모터 속도: " << motor.GetSpeed() << std::endl;

    return 0;
}