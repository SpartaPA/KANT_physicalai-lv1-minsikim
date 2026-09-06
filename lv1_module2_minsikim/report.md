# 문제1. C++ 빌드 체계 세우기 — g++ 다중 파일 빌드와 CMake 전환
답안 템플릿
- 수동 2단계 빌드 명령 (터미널 입력)
- undefined reference 에러 메시지 (출력) — 컴파일 에러와의 차이 설명
컴파일 에러는 main.cpp -> main.o 컴파일 단계에서 에러가 나는것이고, 링크에러는 .o파일들의 링크단계에서 필요한 함수를 찾지못해 생기는 에러이다.
```
s$ g++ main.o -o motor
/usr/bin/ld: main.o: in function `main':
main.cpp:(.text+0x24): undefined reference to `Motor::Motor()'
/usr/bin/ld: main.cpp:(.text+0x3c): undefined reference to `Motor::SetSpeed(double)'
/usr/bin/ld: main.cpp:(.text+0x64): undefined reference to `Motor::GetSpeed()'
collect2: error: ld returned 1 exit status
```
- CMake 빌드 출력 (터미널 출력)
```
$ cd build
$ cmake ..
-- The C compiler identification is GNU 11.4.0
-- The CXX compiler identification is GNU 11.4.0
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Check for working C compiler: /usr/bin/cc - skipped
-- Detecting C compile features
-- Detecting C compile features - done
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Check for working CXX compiler: /usr/bin/c++ - skipped
-- Detecting CXX compile features
-- Detecting CXX compile features - done
-- Configuring done
-- Generating done
-- Build files have been written to: /home/pa18/git/KANT_physicalai-lv1-minsikim/lv1_module2_김민식/cpp_basics/build
```

```
$ make
[ 33%] Building CXX object CMakeFiles/motor_app.dir/main.cpp.o
[ 66%] Building CXX object CMakeFiles/motor_app.dir/motor.cpp.o
[100%] Linking CXX executable motor_app
[100%] Built target motor_app
```
- 증분 빌드 시 재컴파일된 파일: motor.cpp — 판단 근거
motor.cpp.o파일만 빌딩하는 로그 확인
```
$ make
Consolidate compiler generated dependencies of target motor_app
[ 33%] Building CXX object CMakeFiles/motor_app.dir/motor.cpp.o
[ 66%] Linking CXX executable motor_app
[100%] Built target motor_app
```

# 문제3. rclpy 노드 작성 — 거북이 상태 발행자와 구독자
## 답안 템플릿
- /turtle1/pose 필드 구성:
```
x: 5.544444561004639
y: 5.544444561004639
theta: 0.0
linear_velocity: 0.0
angular_velocity: 0.0
```
- ros2 topic hz /turtle_distance 출력: 평균 10.000 Hz
```
average rate: 9.998
min: 0.100s max: 0.100s std dev: 0.00016s window: 12
```
- 구독자 경고 로그 (터미널 출력)
```
[WARN] [1788706472.126889766] [distance_subscriber]: Distance warning: 7.841 m
```
- 구독자 2개 동시 수신 확인 (양쪽 로그)
- 정사각형 주행 캡처 (turtlesim 화면)
![alt text](image.png)
- Ctrl+C 정상 종료 화면 (출력)