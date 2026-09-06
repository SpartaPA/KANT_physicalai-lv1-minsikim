#ifndef SENSOR_HPP
#define SENSOR_HPP

class Sensor
{
public:
    virtual ~Sensor() = default;
    virtual void read() = 0;
};

#endif