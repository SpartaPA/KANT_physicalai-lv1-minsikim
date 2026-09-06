#include "motor.hpp"

Motor::Motor(): _speed(0) {};

double Motor::GetSpeed() {return _speed; };

void Motor::SetSpeed(double speed) { _speed = speed; };