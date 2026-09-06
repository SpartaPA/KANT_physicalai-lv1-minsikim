#include "sensor.hpp"

class Lidar: Sensor
{
public:
    ~Lidar() override;
    void read() override;
};