#ifndef MOTOR_HPP
#define MOTOR_HPP

class Motor
{
private:
    double _speed;
public:
    Motor();
    double GetSpeed();
    void SetSpeed(double speed);
};

#endif