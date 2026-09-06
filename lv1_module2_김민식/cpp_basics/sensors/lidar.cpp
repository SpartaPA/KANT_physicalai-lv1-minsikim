#include "lidar.hpp"
#include <iostream>

Lidar::~Lidar() {
    std::cout << "Lidar destructor\n";
}

void Lidar::read() {
    std::cout << "Lidar read: distance = 0.30 m\n";
}